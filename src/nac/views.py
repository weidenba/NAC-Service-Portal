from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.db.models import Q
from django.urls import reverse_lazy
from dal import autocomplete

from .models import Device, DeviceRoleProd, Area, DeviceRoleInst
from .forms import DeviceForm


class HomePageView(TemplateView):
    template_name = "home.html"


class DeviceListView(ListView):
    model = Device
    template_name = "devices.html"

    def get_queryset(self):
        # only show devices from areas the user is authorized to see
        device_list = Device.objects.filter(area__in=self.request.user.area.all())
        # filter for search results
        query = self.request.GET.get("q")
        if query:
            device_list = device_list.filter(
                Q(name__icontains=query) | Q(appl_NAC_Hostname__icontains=query) |
                Q(appl_NAC_macAddressAIR__icontains=query) | Q(appl_NAC_macAddressCAB__icontains=query)
                | Q(appl_NAC_FQDN__icontains=query))
        return device_list


class DeviceDetailView(DetailView):
    model = Device
    template_name = "device_detail.html"


class DeviceUpdateView(UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "device_edit.html"


class DeviceDeleteView(DeleteView):
    model = Device
    template_name = "device_delete.html"
    success_url = reverse_lazy("devices")


class DeviceCreateView(CreateView):
    model = Device
    template_name = "device_new.html"
    form_class = DeviceForm


class DeviceRoleProdAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DeviceRoleProd.objects.none()

        qs = DeviceRoleProd.objects.all()

#        autocomplete search results
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

#        only show DeviceRoleProd compatible with selected area
        area_pk = self.forwarded.get("area", None)
        if area_pk:
            area = Area.objects.get(pk=area_pk)
            qs = qs.filter(id__in=area.DeviceRoleProd.all())

        return qs


class DeviceRoleInstAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DeviceRoleInst.objects.none()
        qs = DeviceRoleInst.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        area_pk = self.forwarded.get("area", None)
        if area_pk:
            area = Area.objects.get(pk=area_pk)
            qs = qs.filter(id__in=area.DeviceRoleInst.all())
        return qs


class AreaAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Area.objects.none()

        qs = Area.objects.all()

#        only show areas compatible with user
        qs = qs.filter(id__in=self.request.user.area.all())

#        autocomplete search results
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
