from django.shortcuts import render, reverse
import requests
import google.generativeai as genai
from django.http import HttpResponseRedirect, JsonResponse


genai.configure(api_key="AIzaSyCjr-30vvDZoejP_MDDvhYbWCdLw_2XPME")


def search_patents(request):
    if request.method == 'POST':
        
        text = request.POST.get("text")
        
        check_text= "give me only 10 keywords from the given text."

        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(text+check_text)
        return render(request, 'search_results.html', {'results': response.text})
    elif request.method == 'GET':
        return render(request, 'search_form.html')





    #     response = requests.get(f'https://api.gemini.com/v1/search?q={query}&type=patent')
    #     if response.status_code == 200:
    #         return render(request, 'search/search_results.html', {'results': response.json()['results'][0]['title']})
    #     else:
    #         return render(request, 'search/search_results.html', {'error': 'Failed to retrieve results'})
    # return render(request, 'search/search_form.html')