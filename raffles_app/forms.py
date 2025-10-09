from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

# ==============================================================
#  TicketPurchaseForm 
# ==============================================================

class TicketPurchaseForm(forms.Form):
    """
    Formulario para la compra de una boleta.
    Permite especificar manualmente el número o dejarlo vacío
    para que se asigne de manera aleatoria.
    """
    number = forms.IntegerField(
        required=False,
        min_value=1,
        label="Número de boleta (opcional)",
        help_text="Déjalo vacío para asignación aleatoria."
    )

# ==============================================================
#  SignUpForm
# ==============================================================

class SignUpForm(UserCreationForm):
    """
    Formulario de registro de usuario.
    Extiende UserCreationForm para incluir campos de perfil adicionales:
    teléfono, ciudad y documento de identidad.
    """
    phone = forms.CharField(max_length=20, required=False, label="Teléfono")
    city = forms.CharField(max_length=100, required=False, label="Ciudad")
    document_id = forms.CharField(max_length=50, required=False, label="Documento de identidad")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone", "city", "document_id")

    def clean_email(self):
        """
        Valida que el correo no esté ya registrado.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está en uso.")
        return email

    def save(self, commit=True):
        """
        Guarda el usuario y crea su perfil asociado.
        """
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone")
            profile.city = self.cleaned_data.get("city")
            profile.document_id = self.cleaned_data.get("document_id")
            profile.save()

        return user

# ==============================================================
#  ProfileForm 
# ==============================================================

class ProfileForm(forms.ModelForm):
    """
    Formulario básico para la creación o edición de perfil.
    """
    class Meta:
        model = Profile
        fields = ["phone", "city", "document_id", "photo"]


# ==============================================================
#  UserEditForm
# ==============================================================

class UserEditForm(forms.ModelForm):
    """
    Formulario para editar información básica del usuario.
    El email se muestra como solo lectura.
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "readonly": "readonly",
            }),
        }

# ==============================================================
#  ProfileEditForm 
# ==============================================================

class ProfileEditForm(forms.ModelForm):
    """
    Formulario para editar los datos del perfil del usuario.
    """
    class Meta:
        model = Profile
        fields = ["phone", "city", "photo"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

# ==============================================================
#  ContactForm 
# ==============================================================

class ContactForm(forms.Form):
    """
    Formulario de contacto general para el sitio.
    """
    name = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Correo electrónico")
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)
