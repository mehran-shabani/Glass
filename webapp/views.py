from django.shortcuts import render

def clinical_chat_page(request):
    return render(request,'webapp/clinical_chat.html')
