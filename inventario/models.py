from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Videojuego(models.Model):
    class Plataforma(models.TextChoices):
        PC = 'PC', 'PC'
        PS5 = 'PS5', 'PlayStation 5'
        PS4 = 'PS4', 'PlayStation 4'
        XBOX = 'XBOX', 'Xbox'
        SWITCH = 'SWITCH', 'Nintendo Switch'
        OTRO = 'OTRO', 'Otra'

    titulo = models.CharField(max_length=150)
    plataforma = models.CharField(max_length=10, choices=Plataforma.choices)
    genero = models.CharField(max_length=70)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    stock = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} ({self.plataforma})'

    @property
    def margen_ganancia(self):
        """Calcula el margen porcentual de ganancia sobre el precio de compra."""
        if self.precio_compra and self.precio_compra > Decimal('0'):
            margen = ((self.precio_venta - self.precio_compra) / self.precio_compra) * Decimal('100')
            return round(margen, 1)
        return Decimal('0')

    @property
    def stock_badge_class(self):
        if self.stock == 0:
            return 'badge-stock-empty'
        elif self.stock <= 5:
            return 'badge-stock-low'
        return 'badge-stock-ok'

    @property
    def stock_status_text(self):
        if self.stock == 0:
            return 'Agotado'
        elif self.stock <= 5:
            return 'Stock Bajo'
        return 'En Stock'

    @property
    def platform_icon(self):
        icon_map = {
            'PC': 'bi-windows',
            'PS5': 'bi-playstation',
            'PS4': 'bi-playstation',
            'XBOX': 'bi-xbox',
            'SWITCH': 'bi-nintendo-switch',
            'OTRO': 'bi-controller',
        }
        return icon_map.get(self.plataforma, 'bi-controller')

    @property
    def platform_badge_class(self):
        class_map = {
            'PC': 'badge-plat-pc',
            'PS5': 'badge-plat-ps5',
            'PS4': 'badge-plat-ps4',
            'XBOX': 'badge-plat-xbox',
            'SWITCH': 'badge-plat-switch',
            'OTRO': 'badge-plat-other',
        }
        return class_map.get(self.plataforma, 'badge-plat-other')

    class Meta:
        ordering = ['titulo']


class Movimiento(models.Model):
    class Tipo(models.TextChoices):
        COMPRA = 'COMPRA', 'Compra'
        VENTA = 'VENTA', 'Venta'

    videojuego = models.ForeignKey(Videojuego, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=6, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.cantidad * self.precio_unitario

    @property
    def is_venta(self):
        return self.tipo == self.Tipo.VENTA

    class Meta:
        ordering = ['-fecha']
