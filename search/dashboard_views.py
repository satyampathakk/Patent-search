from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import SearchHistory


@login_required
def dashboard_view(request):
    """Display user's search history."""
    query = request.GET.get('q', '')
    
    # Get user's searches
    searches = SearchHistory.objects.filter(user=request.user)
    
    # Apply search filter if query provided
    if query:
        searches = searches.filter(
            Q(search_text__icontains=query) |
            Q(keywords_extracted__icontains=query) |
            Q(analysis_result__icontains=query)
        )
    
    return render(request, 'dashboard.html', {
        'searches': searches,
        'query': query
    })


@login_required
def search_detail_view(request, search_id):
    """Display detailed view of a specific search."""
    search = get_object_or_404(SearchHistory, id=search_id, user=request.user)
    return render(request, 'search_detail.html', {'search': search})


@login_required
def delete_search_view(request, search_id):
    """Delete a search from history."""
    if request.method == 'POST':
        search = get_object_or_404(SearchHistory, id=search_id, user=request.user)
        search.delete()
        messages.success(request, 'Search deleted successfully.')
    return redirect('dashboard')
