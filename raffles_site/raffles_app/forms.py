
from django import forms


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile





class TicketPurchaseForm(forms.Form):
    number = forms.IntegerField(
        required=False,
        min_value=1,
        label="Número de boleta (opcional)",
        help_text="Déjalo vacío para asignación aleatoria."
    )




# class SignUpForm(UserCreationForm):
#     phone = forms.CharField(max_length=20, required=False, label="Teléfono")
#     city = forms.CharField(max_length=100, required=False, label="Ciudad")
#     document_id = forms.CharField(max_length=50, required=False, label="Documento de identidad")

#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2", "phone", "city", "document_id")

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_staff = False       # 🔒 no admin
#         user.is_superuser = False   # 🔒 no superusuario
#         if commit:
#             user.save()
#             # La señal ya crea el Profile, solo actualizamos
#             Profile.objects.filter(user=user).update(
#                 phone=self.cleaned_data.get("phone"),
#                 city=self.cleaned_data.get("city"),
#                 document_id=self.cleaned_data.get("document_id"),
#             )
#         return user


# class SignUpForm(UserCreationForm):
#     phone = forms.CharField(max_length=20, required=False, label="Teléfono")
#     city = forms.CharField(max_length=100, required=False, label="Ciudad")
#     document_id = forms.CharField(max_length=50, required=False, label="Documento de identidad")

#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2", "phone", "city", "document_id")

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Este email ya está en uso.")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_staff = False
#         user.is_superuser = False
#         if commit:
#             user.save()
#             Profile.objects.filter(user=user).update(
#                 phone=self.cleaned_data.get("phone"),
#                 city=self.cleaned_data.get("city"),
#                 document_id=self.cleaned_data.get("document_id"),
#             )
#         return user

class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)
    document_id = forms.CharField(max_length=50, required=False)


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone", "city", "document_id")


    def clean_email(self):
         email = self.cleaned_data.get("email")
         if User.objects.filter(email=email).exists():
             raise forms.ValidationError("Este email ya está en uso.")
         return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            # aseguramos que exista el perfil
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone")
            profile.city = self.cleaned_data.get("city")
            profile.document_id = self.cleaned_data.get("document_id")
            profile.save()
        return user





class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "city", "document_id", "photo"]





class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "readonly": "readonly",   # 👈 no editable
            }),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "city", "photo"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
        
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }



class ContactForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Correo electrónico")
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)