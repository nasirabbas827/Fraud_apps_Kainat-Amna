# ==============================
# IMPORTS
# ==============================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


from nltk.corpus import sentiwordnet as swn
import socket
from .forms import (
    user_registerForm,
    LoginForm,
    UserUpdateForm , ReviewForm
)
from .models import (
    user_register,
    Application,
    Review,
)


# ==============================
# USER AUTHENTICATION VIEWS
# ==============================

def register(request):
    """
    Handles user registration with form validation and file upload support.
    Redirects to 'home' on successful registration.
    """
    if request.method == 'POST':
        form = user_registerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = user_registerForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    Handles user login.
    Uses session to store username after successful authentication.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = user_register.objects.get(username=username)
                if user.password == password:
                    request.session['username'] = username
                    messages.success(request, 'Login successful!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid password.')
            except user_register.DoesNotExist:
                messages.error(request, 'Username does not exist.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """
    Logs out the user by clearing session data.
    Redirects to login page.
    """
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('login')


from django.db.models import Avg, Q

def home(request):
    # Get filter parameters from the URL
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    # Start with all applications and their averages
    apps_query = Application.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        avg_sentiment=Avg('reviews__sentiment_score')
    )

    # Apply Search Filter (Name)
    if search_query:
        apps_query = apps_query.filter(app_name__icontains=search_query)

    # Apply Category Filter
    if category_filter:
        apps_query = apps_query.filter(category=category_filter)

    # Apply Status Filter
    if status_filter:
        apps_query = apps_query.filter(fraud_status=status_filter)

    # Get unique categories for the dropdown menu
    categories = Application.objects.values_list('category', flat=True).distinct()

    return render(request, 'home.html', {
        'applications': apps_query,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter
    })


# # ==============================
# # SENTIMENT ANALYSIS FUNCTION
# # ==============================

def get_sentiment_score(text):
    """
    Analyzes sentiment of text using NLTK's SentiWordNet.
    Uses common-sense filtering to avoid bias from obscure synsets.
    Returns average sentiment score and label (Positive/Negative/Neutral).
    """
    sentiment_score = 0.0
    sentiment_label = "Neutral"
    word_results = []
    total_words_scored = 0

    print(f"\nAnalyzing text: \"{text}\"\n")

    # Clean and split the text (handling case-sensitivity)
    words = text.lower().strip().split()

    for word in words:
        # Get all synsets for the word
        synsets = list(swn.senti_synsets(word))
        
        if not synsets:
            print(f"Word: '{word}' → No SentiWordNet synsets found. Skipping.\n")
            continue

        print(f"Word: '{word}'")
        
        # We limit analysis to the first 2 synsets (the most common meanings)
        # to avoid obscure definitions skewing the data.
        top_synsets = synsets[:2] 
        word_sum = 0.0
        
        for synset in top_synsets:
            pos = synset.pos_score()
            neg = synset.neg_score()
            obj = synset.obj_score()
            word_sentiment = pos - neg
            
            word_sum += word_sentiment
            word_results.append((word, synset.synset.name(), pos, neg, obj, word_sentiment))

            print(f"   Synset: {synset.synset.name()}")
            print(f"    Pos Score: {pos} | Neg Score: {neg} | Word Sentiment: {word_sentiment}")

        # Average the top synsets for this specific word
        sentiment_score += (word_sum / len(top_synsets))
        total_words_scored += 1
        print()

    # Final Calculation based on words processed
    if total_words_scored > 0:
        avg_sentiment_score = sentiment_score / total_words_scored
    else:
        avg_sentiment_score = 0

    # Labeling with a small neutral buffer (0.05) to prevent "False Negatives"
    if avg_sentiment_score > 0.05:
        sentiment_label = "Positive"
    elif avg_sentiment_score < -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # Print final calculation table
    print("Final Calculation Table:")
    print(f"{'Word':<12} {'Synset':<20} {'PosScore':<10} {'NegScore':<10} {'ObjScore':<10} {'WordScore':<15}")
    print("-" * 80)
    for result in word_results:
        word, synset_name, pos, neg, obj, word_sentiment = result
        print(f"{word:<12} {synset_name:<20} {pos:<10.2f} {neg:<10.2f} {obj:<10.2f} {word_sentiment:<15.2f}")

    print(f"\nFinal Sentiment Score: {avg_sentiment_score:.3f}")
    print(f"Final Sentiment Label: {sentiment_label}\n")

    return avg_sentiment_score, sentiment_label


# ==============================
# App DETAILS + Review SUBMISSION VIEW
# ==============================

 


def app_details(request, app_id):
    application = get_object_or_404(Application, app_id=app_id)
    reviews = Review.objects.filter(app=application).order_by('-created_at')

    # Calculate averages
    metrics = reviews.aggregate(
        avg_rating=Avg('rating'),
        avg_sentiment=Avg('sentiment_score')
    )

    username = request.session.get('username')
    user = user_register.objects.filter(username=username).first() if username else None

    if request.method == 'POST' and user:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = user
            review.app = application

            # ----------------------------
            # IP Address Capture
            # ----------------------------
            ip_address = socket.gethostbyname(socket.gethostname())
            review.ip_address = ip_address

            # ----------------------------
            # Fake Review Detection Logic
            # ----------------------------
            user_review_count = Review.objects.filter(
                user=user,
                app=application
            ).count()

            if user_review_count >= 3:
                review.review_type = 'Fake'
            else:
                review.review_type = 'Genuine'

            # ----------------------------
            # Sentiment Analysis
            # ----------------------------
            score, label = get_sentiment_score(review.comment)
            review.sentiment_score = score
            review.sentiment_label = label

            review.save()
            return redirect('app_details', app_id=application.app_id)
    else:
        form = ReviewForm()

    return render(request, 'app_details.html', {
        'application': application,
        'reviews': reviews,
        'form': form,
        'username': username,
        'avg_rating': metrics['avg_rating'] or 0,
        'avg_sentiment': metrics['avg_sentiment'] or 0
    })


# ==============================
# USER PROFILE UPDATE
# ==============================

def update_profile(request):
    """
    Allows logged-in users to update their profile information and photo.
    """
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(user_register, username=username)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('home')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'update_profile.html', {'form': form})



from django.shortcuts import render, redirect
from .models import SystemFeedback, user_register
from .forms import SystemFeedbackForm
from django.contrib import messages

def submit_feedback(request):
    """
    Allows a logged-in user to submit feedback about the system.
    """
    username = request.session.get('username')
    if not username:
        messages.warning(request, "You must be logged in to submit feedback.")
        return redirect('login')

    user = user_register.objects.get(username=username)

    if request.method == 'POST':
        form = SystemFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = user
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('feedback_list')
    else:
        form = SystemFeedbackForm()

    return render(request, 'feedback_form.html', {'form': form, 'username': username})


def feedback_list(request):
    """
    Shows all feedbacks submitted by the logged-in user.
    """
    username = request.session.get('username')
    if not username:
        # Redirect to login if user is not logged in
        return redirect('login')

    user = user_register.objects.get(username=username)
    feedbacks = SystemFeedback.objects.filter(user=user).order_by('-submitted_at')

    return render(request, 'feedback_list.html', {'feedbacks': feedbacks, 'username': username})
