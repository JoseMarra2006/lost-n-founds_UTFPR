from django import forms

from .models import Item

TIPOS_FORM = [('', 'Selecione...'), ('perdido', 'Perdido'), ('encontrado', 'Encontrado')]
CATEGORIAS_FORM = [('', 'Selecione...')] + [
    ('eletronicos', 'Eletrônicos'),
    ('documentos', 'Documentos'),
    ('vestuario', 'Vestuário'),
    ('outros', 'Outros'),
]


class ItemForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=TIPOS_FORM, label='Tipo')
    categoria = forms.ChoiceField(choices=CATEGORIAS_FORM, label='Categoria')

    class Meta:
        model = Item
        fields = ['tipo', 'titulo', 'descricao', 'categoria', 'local', 'foto']
        labels = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'local': 'Local aproximado',
            'foto': 'Foto',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'foto': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto:
            raise forms.ValidationError('A foto é obrigatória.')
        if hasattr(foto, 'content_type') and foto.content_type not in ('image/jpeg', 'image/png'):
            raise forms.ValidationError('Envie uma imagem JPG ou PNG.')
        if foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError('A foto deve ter no máximo 5 MB.')
        return foto