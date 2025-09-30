from .models import Profile
from django import forms


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TicketPurchaseForm(forms.Form):
    number = forms.IntegerField(
        required=False,
        min_value=1,
        label="Número de boleta (opcional)",
        help_text="Déjalo vacío para asignación aleatoria."
    )




class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False, label="Teléfono")
    city = forms.CharField(max_length=100, required=False, label="Ciudad")
    document_id = forms.CharField(max_length=50, required=False, label="Documento de identidad")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone", "city", "document_id")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False       # 🔒 no admin
        user.is_superuser = False   # 🔒 no superusuario
        if commit:
            user.save()
            # La señal ya crea el Profile, solo actualizamos
            Profile.objects.filter(user=user).update(
                phone=self.cleaned_data.get("phone"),
                city=self.cleaned_data.get("city"),
                document_id=self.cleaned_data.get("document_id"),
            )
        return user
