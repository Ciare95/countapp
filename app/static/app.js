// Variables globales
let carrito = []; // Cambiado de const a let para poder modificarlo

// Función para mostrar mensajes flash
function showFlashMessage(message, category) {
    // Verifica si el contenedor existe; si no, lo crea
    let flashContainer = document.querySelector('.flash-message');
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.className = 'container mt-3 flash-message';
        document.querySelector('.p-3').prepend(flashContainer);
    }

    // Crear el mensaje
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Añadir el mensaje al contenedor
    flashContainer.appendChild(alertDiv);

    // Auto-dismiss después de 3 segundos
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}


// Función para formatear números en peso colombiano
function formatoPesoColombianoJS(valor) {
    return new Intl.NumberFormat('es-CO', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(valor);
}

// Buscar productos según el término ingresado
function buscarProducto(termino) {
    if (!termino) {
        document.getElementById('product-suggestions').style.display = 'none';
        return;
    }

    fetch(`/productos/buscar/${termino}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            const suggestions = document.getElementById('product-suggestions');
            suggestions.innerHTML = '';
            data.forEach(producto => {
                const item = document.createElement('li');
                item.classList.add('list-group-item');
                item.textContent = `${producto.nombre} - $${producto.precio}`;
                item.onclick = () => seleccionarProducto(producto);
                suggestions.appendChild(item);
            });
            suggestions.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Error al buscar productos: ' + error.message, 'danger');
        });
}

// Agregar producto seleccionado al carrito
function seleccionarProducto(producto) {
    document.getElementById('product-suggestions').style.display = 'none';
    document.getElementById('producto').value = '';

    const productoExistente = carrito.find(p => p.id === producto.id);
    if (!productoExistente) {
        carrito.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: 1
        });
    } else {
        productoExistente.cantidad += 1;
    }

    actualizarTabla();
}

function actualizarTabla() {
    const tbody = document.getElementById('productos-tabla');
    tbody.innerHTML = '';
    let total = 0;

    if (carrito.length === 0) {
        const noProductosRow = document.createElement('tr');
        const noProductosCell = document.createElement('td');
        noProductosCell.setAttribute('colspan', '5');
        noProductosCell.classList.add('text-center');
        noProductosCell.innerText = 'No hay productos en la tabla';
        noProductosRow.appendChild(noProductosCell);
        tbody.appendChild(noProductosRow);
        document.getElementById('precioTotal').value = "0.00";
        return;
    }

    carrito.forEach((item, index) => {
        const subtotal = item.precio * item.cantidad;
        const tr = document.createElement('tr');
        tr.classList.add('align-middle');
        tr.innerHTML = `
            <td class="text-truncate" style="max-width: 150px;">${item.nombre}</td>
            <td>
                <input type="number" class="form-control form-control-sm" value="${item.cantidad}" 
                    min="1" data-index="${index}" onchange="actualizarCantidad(event)">
            </td>
            <td>
                <input type="number" class="form-control form-control-sm" value="${item.precio}" 
                    min="0" step="100" data-index="${index}" onchange="actualizarPrecio(event)">
            </td>
            <td class="text-start">${formatoPesoColombianoJS(subtotal)}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${index})">Quitar</button>
            </td>
        `;
        tbody.appendChild(tr);
        total += subtotal;
    });

    document.getElementById('precioTotal').value = `${formatoPesoColombianoJS(total)}`;
}

function formatoPesoColombianoJS(valor) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(valor);
}

// Modificar la función de transacción
document.getElementById('transaccion').addEventListener('click', function() {
    // Obtener el precio total
    const precioTotal = document.getElementById('precioTotal').value;
    
    // Mostrar el precio total en el modal
    document.getElementById('precioTotalModal').value = precioTotal;
    
    // Limpiar campos de monto pagado y cambio
    document.getElementById('montoPagado').value = '';
    document.getElementById('cambio').value = '';
    
    // Mostrar el modal
    const transaccionModal = new bootstrap.Modal(document.getElementById('transaccionModal'));
    transaccionModal.show();
});

// Agregar evento de escucha para calcular cambio automáticamente
document.getElementById('montoPagado').addEventListener('input', function() {
    // Limpiar el valor del precio total de caracteres no numéricos
    const precioTotal = parseFloat(document.getElementById('precioTotalModal').value.replace(/[^\d]/g, '')) / 100;
    const montoPagado = parseFloat(this.value);

    if (isNaN(montoPagado)) {
        document.getElementById('cambio').value = '';
        return;
    }

    if (montoPagado < precioTotal) {
        document.getElementById('cambio').value = 'Monto insuficiente';
        return;
    }

    const cambio = montoPagado - precioTotal;
    document.getElementById('cambio').value = `${formatoPesoColombianoJS(cambio)}`;
});

// Nueva función para manejar cambios en el precio
function actualizarPrecio(event) {
    const index = event.target.getAttribute('data-index');
    const nuevoPrecio = parseFloat(event.target.value);
    
    if (isNaN(nuevoPrecio) || nuevoPrecio < 0) {
        event.target.value = carrito[index].precio;
        return;
    }
    
    carrito[index].precio = nuevoPrecio;
    actualizarTabla();
}

// Después de insertar los productos en la tabla con JavaScript
let productosTabla = document.getElementById("productos-tabla");
if (productosTabla.rows.length === 0) {
    let noProductosRow = document.createElement("tr");
    let noProductosCell = document.createElement("td");
    noProductosCell.setAttribute("colspan", "5");
    noProductosCell.classList.add("text-center");
    noProductosCell.innerText = "No hay productos en la tabla";
    noProductosRow.appendChild(noProductosCell);
    productosTabla.appendChild(noProductosRow);
}


function eliminarProducto(index) {
    carrito.splice(index, 1); // Eliminar el producto del carrito
    actualizarTabla(); // Actualizar la tabla después de eliminar el producto
}


function actualizarCantidad(event) {
    const input = event.target;
    const nuevaCantidad = parseInt(input.value) || 1;
    const index = parseInt(input.dataset.index);
    carrito[index].cantidad = nuevaCantidad;
    actualizarTabla();
}

document.getElementById('guardarVentaModal').addEventListener('click', async () => {
    const clienteId = Number(document.getElementById('cliente-select').value);
    const estado = document.getElementById('estado-input').value;
    const montoPagado = parseFloat(document.getElementById('montoPagado').value);
    const total = carrito.reduce((acc, item) => acc + item.precio * item.cantidad, 0);
    const montoAbono = total; // Cambio clave: el abono es exactamente el total
    const saldo = 0; // El saldo es 0 porque se paga completamente

    if (!clienteId || clienteId === '') {
        showFlashMessage('Por favor, selecciona un cliente', 'danger');
        return;
    }

    if (carrito.length === 0) {
        showFlashMessage('Por favor, selecciona productos antes de crear la venta', 'danger');
        return;
    }

    if (montoPagado < total) {
        showFlashMessage('El monto pagado debe ser igual o mayor al total de la venta', 'danger');
        return;
    }

    try {
        const response = await fetch('/ventas/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_cliente: clienteId,
                productos: carrito,
                total: total,
                estado: estado,
                saldo: saldo,
                monto_abono: montoAbono,
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Error al crear la venta');
        }

        showFlashMessage(data.message, data.category);

        if (data.success) {
            // Cerrar modal
            const transaccionModal = bootstrap.Modal.getInstance(document.getElementById('transaccionModal'));
            transaccionModal.hide();

            // Limpiar formulario y carrito
            carrito = [];
            actualizarTabla();
            document.getElementById('producto').value = '';
            document.getElementById('cliente-select').value = '';
            document.getElementById('estado-input').value = 'pendiente';
            document.getElementById('monto-abono').value = '';

            console.log('Venta creada con ID:', data.id_venta);
        }

    } catch (error) {
        showFlashMessage(error.message, 'danger');
    }
});

document.getElementById('crearVentaDirecta').addEventListener('click', async () => {
    const clienteId = Number(document.getElementById('cliente-select').value);
    const estado = document.getElementById('estado-input').value;
    const montoAbono = parseFloat(document.getElementById('monto-abono').value) || 0;
    const total = carrito.reduce((acc, item) => acc + item.precio * item.cantidad, 0);
    const saldo = total - montoAbono;

    if (!clienteId || clienteId === '') {
        showFlashMessage('Por favor, selecciona un cliente', 'danger');
        return;
    }

    if (carrito.length === 0) {
        showFlashMessage('Por favor, selecciona productos antes de crear la venta', 'danger');
        return;
    }

    if (montoAbono > total) {
        showFlashMessage('El abono no puede exceder el total de la venta', 'danger');
        return;
    }

    try {
        const response = await fetch('/ventas/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_cliente: clienteId,
                productos: carrito,
                total: total,
                estado: estado,
                saldo: saldo,
                monto_abono: montoAbono, // Agregar el abono inicial
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Error al crear la venta');
        }

        showFlashMessage(data.message, data.category);

        if (data.success) {
            // Limpiar formulario y carrito
            carrito = [];
            actualizarTabla();
            document.getElementById('producto').value = '';
            document.getElementById('cliente-select').value = '';
            document.getElementById('estado-input').value = 'pendiente';
            document.getElementById('monto-abono').value = '';

            console.log('Venta creada con ID:', data.id_venta);
        }

    } catch (error) {
        showFlashMessage(error.message, 'danger');
    }
});



// Cargar clientes al iniciar
document.addEventListener('DOMContentLoaded', () => {
    fetch('/clientes/api/lista')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('cliente-select');
            select.innerHTML = '';

            if (data.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No hay clientes disponibles';
                select.appendChild(option);
                return;
            }

            data.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;
                option.textContent = `${cliente.nombre} ${cliente.apellido || ''}`;
                select.appendChild(option);
            });

            if (select.options.length > 0) {
                select.value = select.options[0].value;
            }
        })
        .catch(error => {
            showFlashMessage('Error al cargar los clientes: ' + error.message, 'danger');
        });
});
