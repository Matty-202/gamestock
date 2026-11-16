from django import forms
from .models import Videojuego, Movimiento


class VideojuegoForm(forms.ModelForm):
    class Meta:
        model = Videojuego
        fields = ['titulo', 'plataforma', 'genero', 'precio_compra', 'precio_venta', 'stock']
        labels = {
            'titulo': 'Título del Videojuego',
            'plataforma': 'Plataforma',
            'genero': 'Género',
            'precio_compra': 'Precio de Compra ($)',
            'precio_venta': 'Precio de Venta ($)',
            'stock': 'Stock Inicial / Disponible',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-steam',
                'placeholder': 'Ej: Cyberpunk 2077, Elden Ring, God of War...',
                'autocomplete': 'off',
            }),
            'plataforma': forms.Select(attrs={
                'class': 'form-select form-select-steam',
            }),
            'genero': forms.TextInput(attrs={
                'class': 'form-control form-control-steam',
                'placeholder': 'Ej: RPG, Acción, Aventura, Shooter...',
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control form-control-steam',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control form-control-steam',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control form-control-steam',
                'placeholder': '0',
                'min': '0',
            }),
        }

    def clean_titulo(self):
        return self.cleaned_data['titulo'].strip()


class MovimientoForm(forms.Form):
    videojuego = forms.ModelChoiceField(
        queryset=Videojuego.objects.all(),
        label='Videojuego',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-steam',
            'id': 'id_videojuego',
        })
    )
    tipo = forms.ChoiceField(
        choices=Movimiento.Tipo.choices,
        label='Tipo de Operación',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-steam',
            'id': 'id_tipo',
        })
    )
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=1000000,
        label='Cantidad',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-steam',
            'id': 'id_cantidad',
            'min': '1',
            'placeholder': '1',
        })
    )
    precio_unitario = forms.DecimalField(
        min_value=0,
        max_digits=12,
        decimal_places=2,
        label='Precio Unitario ($)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-steam',
            'id': 'id_precio_unitario',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00',
        })
    )
