from django.shortcuts import render

# Create your views here.
def home(request):
	"""The landing page."""
	# return HttpResponse("Hello World!")  # This will also work
	return render(request, "home.html", {})