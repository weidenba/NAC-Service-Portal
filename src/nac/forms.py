from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Device
from django import forms
from django.forms import ModelForm, CheckboxInput
from dal import autocomplete
from .validation import normalize_mac, validate_mac
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ("username", "email", "area",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = ["name",
                  "area",
                  "security_group",
                  "appl_NAC_FQDN",
                  "appl_NAC_Hostname",
                  "appl_NAC_Active",
                  "appl_NAC_ForceDot1X",
                  "appl_NAC_Install",
                  "appl_NAC_AllowAccessCAB",
                  "appl_NAC_AllowAccessAIR",
                  "appl_NAC_AllowAccessVPN",
                  "appl_NAC_AllowAccessCEL",
                  "appl_NAC_DeviceRoleProd",
                  "appl_NAC_DeviceRoleInst",
                  "appl_NAC_macAddressAIR",
                  "appl_NAC_macAddressCAB",
                  "appl_NAC_Certificate",
                  "synchronized",
                  ]

        widgets = {"security_group": autocomplete.ModelSelect2(url="security-group-autocomplete", forward=["area"], ),
                   "area": autocomplete.ModelSelect2(url="area-autocomplete"),
                   "appl_NAC_Active": CheckboxInput,
                   "appl_NAC_ForceDot1X": CheckboxInput,
                   "appl_NAC_Install": CheckboxInput,
                   "appl_NAC_AllowAccessCAB": CheckboxInput,
                   "appl_NAC_AllowAccessAIR": CheckboxInput,
                   "appl_NAC_AllowAccessVPN": CheckboxInput,
                   "appl_NAC_AllowAccessCEL": CheckboxInput,
                   "synchronized": forms.HiddenInput(),
                   }

    def clean(self):
        cleaned_data = super().clean()
        dependencies = {"appl_NAC_ForceDot1X": "appl_NAC_Certificate",
                        "appl_NAC_AllowAccessVPN": "appl_NAC_Certificate",
                        "appl_NAC_AllowAccessAIR": "appl_NAC_macAddressAIR",
                        "appl_NAC_AllowAccessCAB": "appl_NAC_macAddressCAB",
                        }

        for field in dependencies:
            if cleaned_data.get(field) and not cleaned_data.get(dependencies[field]):
                self.add_error(dependencies[field],
                               ValidationError("This field cannot be empty while %(field)s is selected",
                                               params={"field": field}))

    def clean_appl_NAC_macAddressAIR(self):
        data = self.cleaned_data["appl_NAC_macAddressAIR"]
        if not data:
            data = ""
        mac = normalize_mac(data)
        validate_mac(mac)
        return mac

    def clean_appl_NAC_macAddressCAB(self):
        data = self.cleaned_data["appl_NAC_macAddressCAB"]
        if not data:
            data = ""
        data = data.split(",")
        macs = list()
        for item in data:
            mac = normalize_mac(item)
            validate_mac(mac)
            macs.append(mac)
        macs = ",".join(macs)
        return macs

    def clean_synchronized(self):
        return False
