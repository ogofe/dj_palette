from django.contrib import admin
from .site import PaletteAdminSite
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.admin.utils import model_format_dict
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.http import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib import messages
from django.core.exceptions import (
    PermissionDenied
)
from django.contrib.admin.utils import (
    flatten_fieldsets,
    model_format_dict,
    model_ngettext,
    quote,
    unquote,
)
from django.db import models, router, transaction
from django.forms.formsets import all_valid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from functools import partial, update_wrapper
from django.contrib.admin import helpers, widgets





csrf_protect_m = method_decorator(csrf_protect)

class IncorrectLookupParameters(Exception):
    pass


User = get_user_model()

IS_POPUP_VAR = "_popup"
TO_FIELD_VAR = "_to_field"
IS_FACETS_VAR = "_facets"


class PaletteModelAdmin(admin.ModelAdmin):
    grid_display = ("__str__",)
    grid_display_links = ("__str__", )
    detail_view_template = None
    delete_selected_confirmation_template = "admin/delete_confirmation.html"
    delete_confirmation_template = "admin/delete_confirmation.html"
    list_per_page = 15


    def get_urls(self):
        from django.urls import path
        urls:list = super().get_urls()

        
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.opts.app_label, self.opts.model_name


        urls += [
            path(
                "<path:object_id>/",
                wrap(self.detail_view),
                name="%s_%s_view" % info,
            ),
        ]
        return urls

    
    def get_grid_display(self, request):
        """
        Return a sequence containing the fields to be displayed on the
        changelist.
        """
        return self.grid_display


    def get_grid_display_links(self, request, grid_display):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_grid_display().
        """
        if (
            self.grid_display_links
            or self.grid_display_links is None
            or not grid_display
        ):
            return self.grid_display_links
        else:
            # Use only the first item in list_display as link
            return list(grid_display)[:1]
    
    
    def get_sortable_by(self, request):
        """Hook for specifying which fields can be sorted in the changelist."""
        return (
            self.sortable_by
            if self.sortable_by is not None
            else (self.get_list_display(request), self.get_grid_display(request))
        )

    def detail_view(self, request, **kwargs):
        return  #self.delete_queryset


    def get_search_fields(self, request):
        """
        Override get_search_fields to validate and filter out invalid search fields.
        This prevents FieldError when search_fields contains invalid field names.
        """
        search_fields = super().get_search_fields(request)
        
        if not search_fields:
            return []
        
        # Get all valid field names from the model
        valid_field_names = {f.name for f in self.model._meta.get_fields()}
        
        # Filter to only include valid fields and exclude '__str__' which is not a real field
        valid_search_fields = tuple(
            field for field in search_fields 
            if field and field != '__str__' and field in valid_field_names
        )
        
        return valid_search_fields


    def get_changelist(self, request, **kwargs):
        from dj_palette.palette_admin.views import PaletteChangList
        return PaletteChangList
    

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        grid_display = self.get_grid_display(request)
        grid_display_links = self.get_grid_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ["action_checkbox", *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)
        return ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
            self.search_help_text,
            grid_display,
            grid_display_links,
        )
    
    
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        from django.contrib.admin.views.main import ERROR_FLAG

        app_label = self.opts.app_label
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        try:
            cl = self.get_changelist_instance(request)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse(
                    "admin/invalid_setup.html",
                    {
                        "title": _("Database error"),
                    },
                )
            return HttpResponseRedirect(request.path + "?" + ERROR_FLAG + "=1")

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        actions = self.get_actions(request)
        # Actions with no confirmation
        if (
            actions 
            and request.method == "POST"
            and "index" in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _(
                    "Items must be selected in order to perform "
                    "actions on them. No items have been changed."
                )
                self.message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (
            actions
            and request.method == "POST"
            and helpers.ACTION_CHECKBOX_NAME in request.POST
            and "index" not in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == "POST" and cl.list_editable and "_save" in request.POST:
            print("Add Form Submitted")

            if not self.has_change_permission(request):
                raise PermissionDenied
            FormSet = self.get_changelist_formset(request)
            modified_objects = self._get_list_editable_queryset(
                request, FormSet.get_default_prefix()
            )
            formset = cl.formset = FormSet(
                request.POST, request.FILES, queryset=modified_objects
            )
            if formset.is_valid():
                changecount = 0
                with transaction.atomic(using=router.db_for_write(self.model)):
                    for form in formset.forms:
                        if form.has_changed():
                            obj = self.save_form(request, form, change=True)
                            self.save_model(request, obj, form, change=True)
                            self.save_related(request, form, formsets=[], change=True)
                            change_msg = self.construct_change_message(
                                request, form, None
                            )
                            self.log_change(request, obj, change_msg)
                            changecount += 1
                if changecount:
                    msg = ngettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount,
                    ) % {
                        "count": changecount,
                        "name": model_ngettext(self.opts, changecount),
                    }
                    self.message_user(request, msg, messages.SUCCESS)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable and self.has_change_permission(request):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields["action"].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None

        selection_note_all = ngettext(
            "%(total_count)s selected", "All %(total_count)s selected", cl.result_count
        )

        context = {
            **self.admin_site.each_context(request),
            "module_name": str(self.opts.verbose_name_plural),
            "selection_note": _("0 of %(cnt)s selected") % {"cnt": len(cl.result_list)},
            "selection_note_all": selection_note_all % {"total_count": cl.result_count},
            "title": cl.title,
            "subtitle": None,
            "is_popup": cl.is_popup,
            "to_field": cl.to_field,
            "cl": cl,
            "media": media,
            "has_add_permission": self.has_add_permission(request),
            "opts": cl.opts,
            "action_form": action_form,
            "actions_on_top": self.actions_on_top,
            "actions_on_bottom": self.actions_on_bottom,
            "actions_selection_counter": self.actions_selection_counter,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_list_template
            or [
                "admin/%s/%s/change_list.html" % (app_label, self.opts.model_name),
                "admin/%s/change_list.html" % app_label,
                "admin/change_list.html",
            ],
            context,
        )

    
    def _changeform_view(self, request, object_id, form_url, extra_context):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        if request.method == "POST" and "_saveasnew" in request.POST:
            print("Saving as new")
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if request.method == "POST":
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            else:
                if not self.has_view_or_change_permission(request, obj):
                    raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, self.opts, object_id
                )

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )
        if request.method == "POST":
            files = request.FILES
            post_data = request.POST
            # raise Exception("Hello Form Submission!")
            form = ModelForm(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(
                request,
                form.instance,
                change=not add,
            )
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message = self.construct_change_message(
                    request, form, formsets, add
                )
                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(
                    request, form.instance, change=False
                )
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(
                    request, obj, change=True
                )

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        admin_form = helpers.AdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            (
                self.get_prepopulated_fields(request, obj)
                if add or self.has_change_permission(request, obj)
                else {}
            ),
            readonly_fields,
            model_admin=self,
        )
        media = self.media + admin_form.media

        inline_formsets = self.get_inline_formsets(
            request, formsets, inline_instances, obj
        )
        for inline_formset in inline_formsets:
            media += inline_formset.media

        if add:
            title = _("Add %s")
        elif self.has_change_permission(request, obj):
            title = _("Change %s")
        else:
            title = _("View %s")
        context = {
            **self.admin_site.each_context(request),
            "title": title % self.opts.verbose_name,
            "subtitle": str(obj) if obj else None,
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": helpers.AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (
            request.method == "POST"
            and not form_validated
            and "_saveasnew" in request.POST
        ):
            context["show_save"] = False
            context["show_save_and_continue"] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(
            request, context, add=add, change=not add, obj=obj, form_url=form_url
        )

        
class UserModelAdmin(PaletteModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'email', 'last_login')
    list_display_links = ('username', 'first_name', 'email',)
    search_fields = ('username', 'first_name', 'last_name', 'email')


palette_admin = PaletteAdminSite(name='palette_admin')
palette_admin.register(User, UserModelAdmin)
palette_admin.register(Group)
