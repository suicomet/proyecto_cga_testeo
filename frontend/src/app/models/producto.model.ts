export interface Producto {
  id_producto: number;
  nombre_producto: string;
  precio_sugerido: number;
  id_tipo_produccion: number;
  tipo_produccion_nombre?: string;
}