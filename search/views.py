from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .newsc import scrape_patent_data
from .services import AIService
from .models import SearchHistory
import logging
import time

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)


@login_required
def search_patents(request):
    """Handle patent search requests using AI service."""
    if request.method == 'POST':
        start_time = time.time()
        user_idea = request.POST.get("text", "").strip()
        
        logger.info("="*60)
        logger.info("🚀 NEW SEARCH REQUEST STARTED")
        logger.info(f"👤 User: {request.user.username}")
        logger.info(f"💡 Idea: {user_idea[:100]}...")
        logger.info("="*60)
        
        if not user_idea:
            logger.warning("⚠️  Empty search query received")
            messages.error(request, 'Please enter your innovation idea.')
            return render(request, 'search_form.html')
        
        try:
            # Step 1: Initialize AI service
            logger.info("📋 STEP 1/4: Initializing AI Service...")
            step1_start = time.time()
            ai_service = AIService()
            logger.info(f"✅ AI Service initialized in {time.time() - step1_start:.2f}s")
            
            # Step 2: Extract keywords
            logger.info("🔍 STEP 2/4: Extracting Keywords...")
            step2_start = time.time()
            result = ai_service.process_patent_search(user_idea)
            
            if not result['success']:
                logger.error(f"❌ Keyword extraction failed: {result.get('error', 'Unknown error')}")
                messages.error(request, f"Error: {result.get('error', 'Unknown error occurred')}")
                return render(request, 'search_form.html')
            
            keywords = result['keywords']
            logger.info(f"✅ Keywords extracted in {time.time() - step2_start:.2f}s")
            logger.info(f"🔑 Keywords: {keywords}")
            
            # Step 3: Scrape patent data
            logger.info("🌐 STEP 3/4: Searching Patent Database...")
            step3_start = time.time()
            patent_data = scrape_patent_data(keywords)
            logger.info(f"✅ Patent data retrieved in {time.time() - step3_start:.2f}s")
            logger.info(f"📄 Patents found: {len(patent_data.split('Patent ID:')) - 1 if patent_data else 0}")
            
            # Step 4: Analyze similarity
            logger.info("🧠 STEP 4/4: Computing Semantic Similarity & Generating Analysis...")
            step4_start = time.time()
            final_result = ai_service.process_patent_search(user_idea, patent_data)
            
            if not final_result['success']:
                logger.error(f"❌ Analysis failed: {final_result.get('error', 'Unknown error')}")
                messages.error(request, f"Error during analysis: {final_result.get('error', 'Unknown error')}")
                return render(request, 'search_form.html')
            
            logger.info(f"✅ Analysis completed in {time.time() - step4_start:.2f}s")
            
            # Save to database
            logger.info("💾 Saving results to database...")
            save_start = time.time()
            SearchHistory.objects.create(
                user=request.user,
                search_text=user_idea,
                keywords_extracted=keywords,
                patent_data=patent_data,
                analysis_result=final_result['analysis']
            )
            logger.info(f"✅ Results saved in {save_start - time.time():.2f}s")
            
            total_time = time.time() - start_time
            logger.info("="*60)
            logger.info(f"🎉 SEARCH COMPLETED SUCCESSFULLY")
            logger.info(f"⏱️  Total time: {total_time:.2f}s")
            logger.info(f"📊 Analysis length: {len(final_result['analysis'])} chars")
            logger.info(f"🔑 Keywords: {keywords}")
            logger.info("="*60)
            
            # Debug: Log first 200 chars of analysis
            logger.debug(f"Analysis preview: {final_result['analysis'][:200]}...")
            
            return render(request, 'search_results.html', {
                'results': final_result['analysis'],
                'keywords': keywords,
                'user_idea': user_idea
            })
        
        except Exception as e:
            logger.error("="*60)
            logger.error(f"💥 CRITICAL ERROR OCCURRED")
            logger.error(f"❌ Error: {str(e)}")
            logger.error("="*60)
            import traceback
            logger.error(traceback.format_exc())
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'search_form.html')
    
    logger.info("📄 Rendering search form")
    return render(request, 'search_form.html')