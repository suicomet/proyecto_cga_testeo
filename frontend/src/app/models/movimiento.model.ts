export interface DetalleMovimiento {
  id_detalle: number;
  id_jornada: number;
  id_cliente: number;
  id_distribucion: number;
  id_producto: number;
  id_pedido: number | null;
  precio_cobrado: number;
  descuento_porcentaje_aplicado: number | null;
  kilos: number;
  cancelacion: number;
  cliente_nombre?: string;
  producto_nombre?: string;
  distribucion_nombre?: string;
  jornada_fecha?: string;
  venta_linea?: number;
}