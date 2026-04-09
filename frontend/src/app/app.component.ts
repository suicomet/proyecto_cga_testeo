import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" routerLink="/dashboard">Panadería</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link" routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/clientes" routerLinkActive="active">Clientes</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/productos" routerLinkActive="active">Productos</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/pedidos" routerLinkActive="active">Pedidos</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/produccion" routerLinkActive="active">Producción</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/bodega" routerLinkActive="active">Bodega</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/reportes" routerLinkActive="active">Reportes</a>
            </li>
          </ul>
          <button class="btn btn-outline-light" (click)="logout()">Cerrar Sesión</button>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: []
})
export class AppComponent {
  logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
}