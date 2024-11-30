# Three views for entering, viewing, and editing schools
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from mittab.apps.tab.forms import SchoolForm
from mittab.apps.tab.helpers import redirect_and_flash_error, redirect_and_flash_success
from mittab.apps.tab.models import School


def view_schools(request):
    # Get a list of (id,school_name) tuples
    c_schools = [(s.pk, s.name, 0, "") for s in School.objects.all()]
    return render(
        request, "common/list_data.html", {
            "item_type": "school",
            "title": "Viewing All Schools",
            "item_list": c_schools
        })


def view_school(request, school_id):
    school_id = int(school_id)
    try:
        school = School.objects.get(pk=school_id)
    except School.DoesNotExist:
        return redirect_and_flash_error(request, "School not found")
    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            try:
                form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "School name cannot be validated, most likely a non-existent school"
                )
            return redirect_and_flash_success(
                request, "School {} updated successfully".format(
                    form.cleaned_data["name"]))
    else:
        form = SchoolForm(instance=school)
        links = [("/school/" + str(school_id) + "/delete/", "Delete")]
        return render(
            request, "common/data_entry.html", {
                "form": form,
                "links": links,
                "title": "Viewing School: %s" % (school.name)
            })


def enter_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "School name cannot be validated, most likely a duplicate school"
                )
            return redirect_and_flash_success(
                request,
                "School {} created successfully".format(
                    form.cleaned_data["name"]),
                path="/")
    else:
        form = SchoolForm()
    return render(request, "common/data_entry.html", {
        "form": form,
        "title": "Create School"
    })


@permission_required("tab.school.can_delete", login_url="/403/")
def delete_school(request, school_id):
    error_msg = None
    try:
        school_id = int(school_id)
        school = School.objects.get(pk=school_id)
        school.delete()
    except School.DoesNotExist:
        error_msg = "That school does not exist"
    except Exception as e:
        error_msg = str(e)
    if error_msg:
        return redirect_and_flash_error(request, error_msg)
    return redirect_and_flash_success(request,
                                      "School deleted successfully",
                                      path="/")

