import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Turnos
  getTurnos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/turnos/`);
  }

  // Distribuciones
  getDistribuciones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/distribuciones/`);
  }

  // Clientes
  getClientes(): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/`);
  }

  getCliente(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/${id}/`);
  }

  createCliente(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/clientes/`, data);
  }

  updateCliente(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/clientes/${id}/`, data);
  }

  deleteCliente(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/clientes/${id}/`);
  }

  getSaldoCliente(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/${id}/saldo/`);
  }

  // Productos
  getProductos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/productos/`);
  }

  createProducto(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/productos/`, data);
  }

  // Pedidos
  getPedidos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/pedidos/`);
  }

  createPedido(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/pedidos/`, data);
  }

  // Producción
  getProducciones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/producciones/`);
  }

  createProduccion(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/producciones/`, data);
  }

  // Movimientos
  getMovimientos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos/`);
  }

  createMovimiento(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/movimientos/`, data);
  }

  getResumenJornada(jornadaId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos/resumen_jornada/?jornada_id=${jornadaId}`);
  }

  // Bodega
  getMovimientosBodega(): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos-bodega/`);
  }

  createMovimientoBodega(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/movimientos-bodega/`, data);
  }

  // Reportes
  getStockInsumo(insumoId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reportes/stock_insumo/?insumo_id=${insumoId}`);
  }
}