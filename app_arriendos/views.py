from django.shortcuts import render, redirect, get_object_or_404
from .models import Inmuebles, Ubicacion, Usuarios, Direccion, Tipo_usuario
from .forms import RegisterForm, DireccionForm, UbicacionForm, UsuarioForm, UpdateProfileForm, InmuebleForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string


# Vista inicio
def indexView(request):
    inmuebles = None
    tipo_usuario = None

    if request.user.is_authenticated:
        usuario = get_object_or_404(Usuarios, usuario=request.user)
        tipo_usuario = usuario.tipo_usuario.tipo

        if tipo_usuario == 'Arrendatario':
            inmuebles = Inmuebles.objects.filter(estado='Disponible')
        elif tipo_usuario == 'Arrendador':
            inmuebles = Inmuebles.objects.filter(id_user=usuario)

    context = {
        'inmuebles': inmuebles,
        'tipo_usuario': tipo_usuario
    }
    return render(request, 'index.html', context)




#Vista registro
def register_view(request):
    if request.user.is_authenticated:
       return HttpResponseRedirect('/')
    
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        usuario_form = UsuarioForm(request.POST)
        direccion_form = DireccionForm(request.POST)
        ubicacion_form = UbicacionForm(request.POST)
        
        if register_form.is_valid() and usuario_form.is_valid() and direccion_form.is_valid() and ubicacion_form.is_valid():
            # Guarda el formulario de registro
            user = register_form.save()

            # Crea un nuevo objeto de usuario (Usuarios)
            usuario = Usuarios()

            # Asigna el objeto de usuario al campo 'usuario'
            usuario.usuario = user

            # Asigna los campos de nombre, apellido y correo
            usuario.nombre = register_form.cleaned_data['first_name']
            usuario.apellido = register_form.cleaned_data['last_name']
            usuario.correo = register_form.cleaned_data['email']
            usuario.telefono = usuario_form.cleaned_data['telefono']
            usuario.rut = usuario_form.cleaned_data['rut']
            
            # Obtén el tipo de usuario seleccionado del formulario
            tipo_usuario_elegido = usuario_form.cleaned_data['tipo_usuario']

            # Asigna el tipo de usuario al objeto de usuario
            usuario.tipo_usuario = tipo_usuario_elegido

            # Obtén la ubicación seleccionada del formulario
            ubicacion_elegida = ubicacion_form.cleaned_data['comuna_region']

            # Busca el objeto de ubicación correspondiente
            ubicacion = Ubicacion.objects.get(id_ubicacion=ubicacion_elegida.id_ubicacion)

            # Guarda la ubicación en la tabla de direcciones
            direccion = direccion_form.save(commit=False)
            direccion.id_ubicacion = ubicacion
            direccion.save()

            # Asigna la dirección al usuario y luego lo guarda
            usuario.id_direccion = direccion
            usuario.save()

            #mensaje de Usuario Registrado
            messages.success(request, 'Usuario registrado exitosamente.')

            #Inicio de sesión con ultimo usuario registrado
            username = register_form.cleaned_data["username"]
            password = register_form.cleaned_data["password1"]
            ultimo_usuario_creado = authenticate(request, username=username, password=password)
            if ultimo_usuario_creado:
                login(request, ultimo_usuario_creado)  
                return redirect('home')
            return HttpResponseRedirect('/')
        context = {
            'register_form': register_form,
            'usuario_form': usuario_form,
            'direccion_form': direccion_form,
            'ubicacion_form': ubicacion_form
            }
        return render(request, 'registration/register.html', context)

    else:
        register_form = RegisterForm()
        usuario_form = UsuarioForm()
        direccion_form = DireccionForm()
        ubicacion_form = UbicacionForm()    
        context = {
            'register_form': register_form,
            'usuario_form': usuario_form,
            'direccion_form': direccion_form,
            'ubicacion_form': ubicacion_form
            }
        return render(request, 'registration/register.html', context)
    
    
@login_required
def perfil_usuario(request):
    usuario = request.user
    tipo = Usuarios.objects.get(usuario=usuario).tipo_usuario.tipo

    perfil = Usuarios.objects.filter(usuario=usuario).first()

    if perfil:
        direccion = perfil.id_direccion
    else:
        direccion = None
        # Manejar la excepción si no se encuentra el perfil

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'tipo': tipo,
        'direccion': direccion
    }
    return render(request, 'perfil_usuario.html', context)



@login_required
def editar_perfil(request):
    usuario = request.user
    perfil = Usuarios.objects.filter(usuario=usuario).first()

    if perfil:
        direccion = perfil.id_direccion
    else:
        direccion = None

    if request.method == 'POST':
        update_form = UpdateProfileForm(request.POST, instance=usuario)
        usuario_form = UsuarioForm(request.POST, instance=perfil)
        direccion_form = DireccionForm(request.POST, instance=direccion)
        ubicacion_form = UbicacionForm(request.POST, instance=direccion)

        if update_form.is_valid() and usuario_form.is_valid() and direccion_form.is_valid() and ubicacion_form.is_valid():
            # Guarda la ubicación en la tabla de direcciones
            direccion = direccion_form.save(commit=False)
            direccion.save()

            # Asigna la dirección al usuario y luego lo guarda
            usuario.id_direccion = direccion
            usuario.save()
            
            direccion.save()
            return redirect('perfil_usuario')
    else:
        update_form = UpdateProfileForm(instance=usuario)
        usuario_form = UsuarioForm(instance=perfil)
        direccion_form = DireccionForm(instance=direccion)
        ubicacion_form = UbicacionForm(instance=direccion)

    context = {
        'update_form': update_form,
        'usuario_form': usuario_form,
        'direccion_form': direccion_form,
        'ubicacion_form': ubicacion_form
        }
    return render(request, 'editar_perfil.html', context)

@login_required
def agregar_inmueble(request):
    if request.method == 'POST':
        inmueble_form = InmuebleForm(request.POST)
        direccion_form = DireccionForm(request.POST)
        ubicacion_form = UbicacionForm(request.POST)

        if inmueble_form.is_valid() and direccion_form.is_valid() and ubicacion_form.is_valid():
            # Obtener la ubicación seleccionada del formulario
            ubicacion_elegida = ubicacion_form.cleaned_data['comuna_region']

            # Buscar el objeto de ubicación correspondiente
            ubicacion = Ubicacion.objects.get(id_ubicacion=ubicacion_elegida.id_ubicacion)

            # Guarda la ubicación en la tabla de direcciones
            direccion = direccion_form.save(commit=False)
            direccion.id_ubicacion = ubicacion
            direccion.save()

            inmueble = inmueble_form.save(commit=False)
            inmueble.id_user = request.user.usuarios
            inmueble.id_direccion = direccion
            inmueble.save()
            
            return redirect('home')  # Redirigir al perfil del usuario después de agregar el inmueble
    else:
        inmueble_form = InmuebleForm()
        direccion_form = DireccionForm()
        ubicacion_form = UbicacionForm()

    context = {
        'inmueble_form': inmueble_form,
        'direccion_form': direccion_form,
        'ubicacion_form': ubicacion_form
    }
    return render(request, 'agregar_inmueble.html', context)

@login_required
def editar_inmueble(request, id):
    inmueble = get_object_or_404(Inmuebles, id_inmueble=id)

    if inmueble:
        direccion = inmueble.id_direccion
        ubicacion = direccion.id_ubicacion
    else:
        direccion = None
        ubicacion = None

    if request.method == 'POST':
        inmueble_form = InmuebleForm(request.POST, instance=inmueble)
        direccion_form = DireccionForm(request.POST, instance=direccion)
        ubicacion_form = UbicacionForm(request.POST, instance=ubicacion)

        if inmueble_form.is_valid() and direccion_form.is_valid() and ubicacion_form.is_valid():
            ubicacion = ubicacion_form.save()
            direccion = direccion_form.save(commit=False)
            direccion.id_ubicacion = ubicacion
            direccion.save()
            inmueble_form.save()
            return redirect('home')
    else:
        inmueble_form = InmuebleForm(instance=inmueble)
        direccion_form = DireccionForm(instance=direccion)
        ubicacion_form = UbicacionForm(instance=ubicacion)

    context = {
        'inmueble_form': inmueble_form,
        'direccion_form': direccion_form,
        'ubicacion_form': ubicacion_form
    }
    return render(request, 'editar_inmueble.html', context)



@login_required
def borrar_inmueble(request, id):
    inmueble = get_object_or_404(Inmuebles, id_inmueble=id)
    if request.method == 'POST':
        inmueble.delete()
        return redirect('home')

    return render(request, 'borrar_inmueble.html', {'inmueble': inmueble})


def listar_inmuebles(request):
    inmuebles = Inmuebles.objects.filter(estado='Disponible')
    return render(request, 'listar_inmuebles.html', {'inmuebles': inmuebles})


def detalle_inmueble(request, id):
    inmueble = get_object_or_404(Inmuebles, id_inmueble=id)
    context = {
        'inmueble': inmueble
    }
    return render(request, 'detalle_inmueble.html', context)

# def load_comunas(request):
#      region_name = request.GET.get('region_name')
#      comunas = Ubicacion.objects.filter(nombre_region=region_name).values_list('nombre_comuna', flat=True)
#      return JsonResponse(render_to_string('comunas_dropdown_list_options.html', {'comunas': comunas}), safe=False)