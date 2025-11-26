from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.main import ChangeList
from .models import AdminPage, Component
import json

@staff_member_required
def dashboard_view(request):
    return render(request, 'palette/dashboard.html', {
        "card_component": "card"
    })

@staff_member_required
def dynamic_admin_page(request, slug):
    page = get_object_or_404(AdminPage, slug=slug)
    try:
        layout = json.loads(page.layout_json)
    except json.JSONDecodeError:
        layout = []

    return render(request, 'palette/dynamic_page.html', {
        "page": page,
        "layout": layout
    })

@staff_member_required
@csrf_protect
def edit_admin_page(request, slug):
	try:
		page = get_object_or_404(AdminPage, slug=slug)
		components = Component.objects.all()

		if request.method == "POST":
			page.layout_json = request.POST.get("layout_json", "")
			page.save()
			return redirect("palette:edit-admin-page", slug=slug)

		return render(request, "palette/edit_page.html", {
			"page": page,
			"components": components
		})
	except:
		return render(request, "palette/edit_page.html", {
			"page": None,
			"components": []
		})



class PaletteChangList(ChangeList):
      
	def __init__(self, request, grid_display, grid_display_links, grid_actions, **kwargs):
		self.grid_display = grid_display
		self.grid_display_links = grid_display_links
		self.grid_actions = grid_actions
		super().__init__(**kwargs)

	

	
	


