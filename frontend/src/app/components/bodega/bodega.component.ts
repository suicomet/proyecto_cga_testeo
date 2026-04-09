import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-bodega',
  templateUrl: './bodega.component.html',
  styleUrls: ['./bodega.component.css']
})
export class BodegaComponent implements OnInit {
  movimientos: any[] = [];
  nuevoMovimiento: any = {
    tipo_movimiento: 'ENTRADA'
  };
  mostrarForm = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarMovimientos();
  }

  cargarMovimientos() {
    this.apiService.getMovimientosBodega().subscribe(data => {
      this.movimientos = Array.isArray(data) ? data : data.results || data;
    });
  }

  crearMovimiento() {
    this.apiService.createMovimientoBodega(this.nuevoMovimiento).subscribe(() => {
      this.cargarMovimientos();
      this.nuevoMovimiento = { tipo_movimiento: 'ENTRADA' };
      this.mostrarForm = false;
    });
  }
}