from django import forms
from django.contrib.auth.models import User

class CadastroForm(UserCreationForm):
    first_name = form.CharField(label='Nome', max_length=50)
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        usuario.email = self.cleaned_data['email']
        usuario.first_name = self.cleaned_data['first_name']
        if commit:
            usuario.save()
        return usuario