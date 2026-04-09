import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-produccion',
  templateUrl: './produccion.component.html',
  styleUrls: ['./produccion.component.css']
})
export class ProduccionComponent implements OnInit {
  producciones: any[] = [];
  nuevaProduccion: any = {
    quintales: 0
  };
  mostrarForm = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarProducciones();
  }

  cargarProducciones() {
    this.apiService.getProducciones().subscribe(data => {
      this.producciones = Array.isArray(data) ? data : data.results || data;
    });
  }

  crearProduccion() {
    this.apiService.createProduccion(this.nuevaProduccion).subscribe(() => {
      this.cargarProducciones();
      this.nuevaProduccion = { quintales: 0 };
      this.mostrarForm = false;
    });
  }
}