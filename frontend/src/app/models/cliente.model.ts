export interface Cliente {
  id_cliente: number;
  rut: string;
  digito_verificador: string;
  nombre_cliente: string;
  ciudad: string;
  direccion: string;
  telefono: string;
  descuento_aplicado: number | null;
}