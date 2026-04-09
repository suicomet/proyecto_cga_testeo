import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Cliente } from '../../models/cliente.model';

@Component({
  selector: 'app-clientes',
  templateUrl: './clientes.component.html',
  styleUrls: ['./clientes.component.css']
})
export class ClientesComponent implements OnInit {
  clientes: Cliente[] = [];
  clienteEdit: Cliente | null = null;
  nuevoCliente: Partial<Cliente> = {};
  mostrarForm = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarClientes();
  }

  cargarClientes() {
    this.apiService.getClientes().subscribe(data => {
      this.clientes = Array.isArray(data) ? data : data.results || data;
    });
  }

  crearCliente() {
    this.apiService.createCliente(this.nuevoCliente).subscribe(() => {
      this.cargarClientes();
      this.nuevoCliente = {};
      this.mostrarForm = false;
    });
  }

  editarCliente(cliente: Cliente) {
    this.clienteEdit = { ...cliente };
  }

  actualizarCliente() {
    if (this.clienteEdit) {
      this.apiService.updateCliente(this.clienteEdit.id_cliente, this.clienteEdit).subscribe(() => {
        this.cargarClientes();
        this.clienteEdit = null;
      });
    }
  }

  eliminarCliente(id: number) {
    if (confirm('¿Está seguro de eliminar este cliente?')) {
      this.apiService.deleteCliente(id).subscribe(() => {
        this.cargarClientes();
      });
    }
  }
}