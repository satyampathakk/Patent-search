from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .newsc import scrape_patent_data
from .services import AIService
from .models import SearchHistory


@login_required
def search_patents(request):
    """Handle patent search requests using AI service."""
    if request.method == 'POST':
        user_idea = request.POST.get("text", "").strip()
        
        if not user_idea:
            messages.error(request, 'Please enter your innovation idea.')
            return render(request, 'search_form.html')
        
        try:
            # Initialize AI service
            ai_service = AIService()
            
            # Extract keywords
            result = ai_service.process_patent_search(user_idea)
            
            if not result['success']:
                messages.error(request, f"Error: {result.get('error', 'Unknown error occurred')}")
                return render(request, 'search_form.html')
            
            keywords = result['keywords']
            
            # Scrape patent data using keywords
            patent_data = scrape_patent_data(keywords)
            
            # Analyze similarity with patent data
            final_result = ai_service.process_patent_search(user_idea, patent_data)
            
            if not final_result['success']:
                messages.error(request, f"Error during analysis: {final_result.get('error', 'Unknown error')}")
                return render(request, 'search_form.html')
            
            # Save to database
            SearchHistory.objects.create(
                user=request.user,
                search_text=user_idea,
                keywords_extracted=keywords,
                patent_data=patent_data,
                analysis_result=final_result['analysis']
            )
            
            return render(request, 'search_results.html', {
                'results': final_result['analysis'],
                'keywords': keywords,
                'user_idea': user_idea
            })
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'search_form.html')
    
    return render(request, 'search_form.html')