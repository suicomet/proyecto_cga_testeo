import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-reportes',
  templateUrl: './reportes.component.html',
  styleUrls: ['./reportes.component.css']
})
export class ReportesComponent {
  insumoId = 1;
  stockInfo: any = null;

  constructor(private apiService: ApiService) {}

  consultarStock() {
    this.apiService.getStockInsumo(this.insumoId).subscribe(data => {
      this.stockInfo = data;
    });
  }
}