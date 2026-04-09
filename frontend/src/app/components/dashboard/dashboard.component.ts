import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  stats = {
    totalClientes: 0,
    totalProductos: 0,
    pedidosHoy: 0,
    produccionHoy: 0
  };

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadStats();
  }

  loadStats() {
    this.http.get<any>(`${environment.apiUrl}/clientes/`).subscribe(data => {
      this.stats.totalClientes = data.count || data.length;
    });
    this.http.get<any>(`${environment.apiUrl}/productos/`).subscribe(data => {
      this.stats.totalProductos = data.count || data.length;
    });
    // Aquí se podrían agregar más llamadas para pedidos y producción del día
  }
}