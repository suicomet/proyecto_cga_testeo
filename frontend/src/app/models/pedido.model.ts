export interface Pedido {
  id_pedido: number;
  id_cliente: number;
  id_distribucion: number;
  fecha_pedido: string;
  fecha_entrega_solicitada: string;
  cliente_nombre?: string;
  distribucion_nombre?: string;
  detalles?: DetallePedido[];
}

export interface DetallePedido {
  id_detalle_pedido: number;
  id_pedido: number;
  id_producto: number;
  cantidad_solicitada: number;
  precio_cobrado: number;
  descuento_porcentaje_aplicado: number | null;
  producto_nombre?: string;
}