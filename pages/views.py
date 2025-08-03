from django.shortcuts import render

def about(request):
    return render(request, 'pages/about.html')

def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'pages/terms_of_service.html')

def contact(request):
    return render(request, 'pages/contact.html')

def faq(request):
    return render(request, 'pages/faq.html')

def sitemap(request):
    return render(request, 'pages/sitemap.html') 