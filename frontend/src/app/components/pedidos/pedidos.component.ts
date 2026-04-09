import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Pedido } from '../../models/pedido.model';

@Component({
  selector: 'app-pedidos',
  templateUrl: './pedidos.component.html',
  styleUrls: ['./pedidos.component.css']
})
export class PedidosComponent implements OnInit {
  pedidos: Pedido[] = [];
  nuevoPedido: Partial<Pedido> = {
    fecha_pedido: new Date().toISOString().split('T')[0],
    fecha_entrega_solicitada: new Date().toISOString().split('T')[0]
  };
  mostrarForm = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarPedidos();
  }

  cargarPedidos() {
    this.apiService.getPedidos().subscribe(data => {
      this.pedidos = Array.isArray(data) ? data : data.results || data;
    });
  }

  crearPedido() {
    this.apiService.createPedido(this.nuevoPedido).subscribe(() => {
      this.cargarPedidos();
      this.nuevoPedido = {
        fecha_pedido: new Date().toISOString().split('T')[0],
        fecha_entrega_solicitada: new Date().toISOString().split('T')[0]
      };
      this.mostrarForm = false;
    });
  }
}