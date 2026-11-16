import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F, Q, Count, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Videojuego, Movimiento
from .forms import VideojuegoForm, MovimientoForm


@login_required
def inicio(request):
    ventas = Movimiento.objects.filter(tipo='VENTA')
    compras = Movimiento.objects.filter(tipo='COMPRA')

    def calc_total(qs):
        return sum((m.total for m in qs), Decimal('0'))

    total_ventas = calc_total(ventas)
    total_compras = calc_total(compras)

    # Datos para gráficos (Stock por plataforma)
    plat_qs = (
        Videojuego.objects.values('plataforma')
        .annotate(total_stock=Sum('stock'), total_juegos=Count('id'))
        .order_by('-total_stock')
    )
    labels_plataforma = []
    datos_stock_plataforma = []
    display_names = dict(Videojuego.Plataforma.choices)
    for p in plat_qs:
        labels_plataforma.append(display_names.get(p['plataforma'], p['plataforma']))
        datos_stock_plataforma.append(p['total_stock'] or 0)

    # Indicadores adicionales
    total_juegos = Videojuego.objects.count()
    unidades_disponibles = Videojuego.objects.aggregate(s=Sum('stock'))['s'] or 0
    bajo_stock_count = Videojuego.objects.filter(stock__gt=0, stock__lte=5).count()
    agotados_count = Videojuego.objects.filter(stock=0).count()

    context = {
        'productos': total_juegos,
        'unidades': unidades_disponibles,
        'ventas': total_ventas,
        'compras': total_compras,
        'ultimos': Movimiento.objects.select_related('videojuego', 'usuario')[:8],
        'ventas_count': ventas.count(),
        'compras_count': compras.count(),
        'bajo_stock_count': bajo_stock_count,
        'agotados_count': agotados_count,
        'chart_plat_labels': json.dumps(labels_plataforma),
        'chart_plat_data': json.dumps(datos_stock_plataforma),
        'chart_fin_labels': json.dumps(['Ventas', 'Compras']),
        'chart_fin_data': json.dumps([float(total_ventas), float(total_compras)]),
    }
    return render(request, 'inventario/inicio.html', context)


@login_required
def catalogo(request):
    q = request.GET.get('q', '').strip()[:100]
    plataforma = request.GET.get('plataforma', '').strip()
    genero = request.GET.get('genero', '').strip()[:70]

    juegos = Videojuego.objects.all()
    if q:
        juegos = juegos.filter(Q(titulo__icontains=q) | Q(genero__icontains=q))
    if plataforma in Videojuego.Plataforma.values:
        juegos = juegos.filter(plataforma=plataforma)
    if genero:
        juegos = juegos.filter(genero__iexact=genero)

    # Lista de géneros únicos para filtro rápido
    generos_disponibles = Videojuego.objects.values_list('genero', flat=True).distinct().order_by('genero')

    context = {
        'juegos': juegos,
        'q': q,
        'plataforma': plataforma,
        'genero': genero,
        'plataformas': Videojuego.Plataforma.choices,
        'generos_disponibles': [g for g in generos_disponibles if g],
        'total_mostrados': juegos.count(),
    }
    return render(request, 'inventario/catalogo.html', context)


@login_required
@permission_required('inventario.add_videojuego', raise_exception=True)
def crear(request):
    form = VideojuegoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '¡Videojuego registrado exitosamente!')
        return redirect('catalogo')
    return render(request, 'inventario/form.html', {
        'form': form,
        'titulo': 'Agregar Videojuego',
        'subtitulo': 'Registra un nuevo título en el catálogo de GameStock',
        'es_movimiento': False,
    })


@login_required
@permission_required('inventario.change_videojuego', raise_exception=True)
def editar(request, pk):
    juego = get_object_or_404(Videojuego, pk=pk)
    form = VideojuegoForm(request.POST or None, instance=juego)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'¡Videojuego "{juego.titulo}" actualizado correctamente!')
        return redirect('catalogo')
    return render(request, 'inventario/form.html', {
        'form': form,
        'titulo': 'Editar Videojuego',
        'subtitulo': f'Modificando los datos de {juego.titulo}',
        'juego': juego,
        'es_movimiento': False,
    })


@login_required
@permission_required('inventario.delete_videojuego', raise_exception=True)
@require_POST
def eliminar(request, pk):
    juego = get_object_or_404(Videojuego, pk=pk)
    try:
        juego.delete()
        messages.success(request, f'Videojuego "{juego.titulo}" eliminado con éxito.')
    except ProtectedError:
        messages.error(request, 'Acción bloqueada: Este videojuego tiene movimientos históricos asociados y no puede ser eliminado.')
    return redirect('catalogo')


@login_required
@permission_required('inventario.add_movimiento', raise_exception=True)
def registrar(request):
    form = MovimientoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        with transaction.atomic():
            juego = d['videojuego']
            cantidad = d['cantidad']
            if d['tipo'] == 'VENTA':
                actualizados = Videojuego.objects.filter(pk=juego.pk, stock__gte=cantidad).update(stock=F('stock') - cantidad)
                if not actualizados:
                    form.add_error('cantidad', f'Stock insuficiente: Solo hay {juego.stock} unidades disponibles de {juego.titulo}.')
            else:
                Videojuego.objects.filter(pk=juego.pk).update(stock=F('stock') + cantidad)

            if not form.errors:
                Movimiento.objects.create(
                    videojuego=juego,
                    tipo=d['tipo'],
                    cantidad=cantidad,
                    precio_unitario=d['precio_unitario'],
                    usuario=request.user,
                )
                tipo_str = "Venta registrada" if d['tipo'] == 'VENTA' else "Compra registrada"
                messages.success(request, f'¡{tipo_str} exitosamente para {juego.titulo} ({cantidad} uds.)!')
                return redirect('historial')

    # Diccionario de juegos con datos para pre-llenar precio y mostrar stock
    juegos_meta = {
        str(j.pk): {
            'stock': j.stock,
            'precio_compra': str(j.precio_compra),
            'precio_venta': str(j.precio_venta),
            'titulo': j.titulo,
            'plataforma': j.get_plataforma_display(),
        }
        for j in Videojuego.objects.all()
    }

    return render(request, 'inventario/form.html', {
        'form': form,
        'titulo': 'Registrar Operación de Inventario',
        'subtitulo': 'Gestión de entrada (Compra) o salida (Venta) con actualización automática de stock',
        'es_movimiento': True,
        'juegos_meta_json': json.dumps(juegos_meta),
    })


@login_required
def historial(request):
    tipo_filtro = request.GET.get('tipo', '').strip().upper()
    movimientos = Movimiento.objects.select_related('videojuego', 'usuario')

    if tipo_filtro in ['COMPRA', 'VENTA']:
        movimientos = movimientos.filter(tipo=tipo_filtro)

    movimientos_list = list(movimientos[:200])

    total_compras = sum((m.total for m in movimientos_list if m.tipo == 'COMPRA'), Decimal('0'))
    total_ventas = sum((m.total for m in movimientos_list if m.tipo == 'VENTA'), Decimal('0'))

    return render(request, 'inventario/historial.html', {
        'movimientos': movimientos_list,
        'tipo_filtro': tipo_filtro,
        'total_registros': len(movimientos_list),
        'total_compras': total_compras,
        'total_ventas': total_ventas,
    })
