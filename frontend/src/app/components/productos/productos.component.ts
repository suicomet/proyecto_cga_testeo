import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Producto } from '../../models/producto.model';

@Component({
  selector: 'app-productos',
  templateUrl: './productos.component.html',
  styleUrls: ['./productos.component.css']
})
export class ProductosComponent implements OnInit {
  productos: Producto[] = [];
  nuevoProducto: Partial<Producto> = {};
  mostrarForm = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarProductos();
  }

  cargarProductos() {
    this.apiService.getProductos().subscribe(data => {
      this.productos = Array.isArray(data) ? data : data.results || data;
    });
  }

  crearProducto() {
    this.apiService.createProducto(this.nuevoProducto).subscribe(() => {
      this.cargarProductos();
      this.nuevoProducto = {};
      this.mostrarForm = false;
    });
  }
}