# history_csv.py
import os
import csv
from datetime import datetime
import conexion

class TraceabilityManager:
    def __init__(self, base_path=None, max_records=100):
        """
        Inicializa el gestor de trazabilidad
        
        Args:
            base_path: Ruta base donde se almacenarán los archivos
            max_records: Número máximo de registros por archivo
        """
        if base_path is None:
            try:
                import getpass
                usuario = getpass.getuser()
                base_path = f"C:/Users/{usuario}/Documents/Traceability"
            except:
                base_path = "C:/Traceability"
        
        self.base_path = base_path
        self.max_records = max_records
        self.current_date = None
        self.current_file_path = None
        self.records_count = 0
        self.max_columns = 0  # Guarda el máximo número de columnas visto
        
    def _get_date_path(self):
        """Obtiene la ruta para la fecha actual"""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        return os.path.join(self.base_path, year, month, day)
    
    def _ensure_directory_exists(self, path):
        """Asegura que el directorio exista"""
        os.makedirs(path, exist_ok=True)
    
    def _get_file_path(self):
        """Obtiene la ruta del archivo CSV para la fecha actual"""
        date_path = self._get_date_path()
        self._ensure_directory_exists(date_path)
        
        try:
            stationName_data = conexion.model()
            print(stationName_data)
            stationName = stationName_data[2][0]
        except:
            stationName = "Station"
        
        fecha_formateada = datetime.now().strftime("%d%m%y")
        
        return os.path.join(date_path, f"{stationName} {fecha_formateada} 3DAVIData.csv")
    
    def _get_fieldnames(self, num_steps):
        """
        Genera los nombres de campo para el CSV basado en la cantidad de pasos
        Cada paso genera 5 columnas con números consecutivos
        
        Args:
            num_steps: Número de pasos
            
        Returns:
            list: Lista de nombres de campo
        """
        fieldnames = ['Tiempo', 'SN', 'Overall result']
        
        # Generar columnas para cada paso con número
        for i in range(1, num_steps + 1):
            fieldnames.extend([
                f'heightName_{i}',
                f'heightResult_{i}',
                f'heightLimitUp_{i}',
                f'heightLimitDown_{i}',
                f'heightValue_{i}'
            ])
        
        return fieldnames
    
    def _get_existing_records(self, file_path):
        """Lee los registros existentes del archivo CSV"""
        records = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    records = list(reader)
                    # Actualizar el máximo de columnas con las del archivo existente
                    if records:
                        existing_fieldnames = list(records[0].keys())
                        current_max = len(existing_fieldnames)
                        if current_max > self.max_columns:
                            self.max_columns = current_max
            except Exception as e:
                print(f"Error al leer archivo CSV: {e}")
        return records
    
    def _write_records(self, file_path, records, fieldnames):
        """Escribe los registros en el archivo CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Escribir cada registro
                for record in records:
                    # Asegurar que el registro tenga todos los campos
                    row = {}
                    for field in fieldnames:
                        row[field] = record.get(field, '')
                    writer.writerow(row)
                    
            return True
        except Exception as e:
            print(f"Error al escribir archivo CSV: {e}")
            return False
    
    def save_traceability(self, sn, overall_result, steps_list, start_time, end_time):
        """
        Guarda la trazabilidad registrando CADA PASO como columnas en el CSV
        Las columnas tienen números (heightName_1, heightName_2, etc.)
        NO se pierden datos: siempre se mantiene el máximo número de columnas
        
        Args:
            sn: Número de serie
            overall_result: Resultado general (PASS/FAILED)
            steps_list: Lista de pasos de inspección
            start_time: Tiempo de inicio
            end_time: Tiempo de fin
            
        Returns:
            bool: True si se guardó correctamente
        """
        if not steps_list:
            print("ℹ️ No hay pasos para registrar en trazabilidad")
            return False
        
        print(f"\n{'='*60}")
        print(f"📝 GUARDANDO TRAZABILIDAD")
        print(f"{'='*60}")
        print(f"   SN: {sn}")
        print(f"   Overall result: {overall_result}")
        print(f"   Total pasos a registrar: {len(steps_list)}")
        print(f"   Fecha inicio: {start_time}")
        print(f"   Fecha fin: {end_time}")
        
        # Usar start_time como timestamp
        timestamp = start_time
        
        # Verificar si cambió la fecha
        current_date = datetime.now().strftime("%Y%m%d")
        if self.current_date != current_date:
            self.current_date = current_date
            self.current_file_path = self._get_file_path()
            self.records_count = 0
            self.max_columns = 0  # Reiniciar máximo de columnas al cambiar de fecha
            print(f"   📁 Nueva fecha: {current_date}")
        
        # Leer registros existentes
        existing_records = self._get_existing_records(self.current_file_path)
        print(f"   📄 Registros existentes: {len(existing_records)}")
        
        # Determinar el número de pasos para el archivo (el máximo entre el actual y los existentes)
        num_pasos_actual = len(steps_list)
        
        # Si hay registros existentes, obtener el número de pasos del archivo existente
        if existing_records:
            existing_fieldnames = list(existing_records[0].keys())
            # Calcular cuántos pasos tiene el archivo existente
            # Restamos 3 por las columnas fijas (Tiempo, SN, Overall result)
            pasos_existentes = (len(existing_fieldnames) - 3) // 5
            print(f"   📋 Pasos en archivo existente: {pasos_existentes}")
            
            # Usar el máximo entre los pasos actuales y los existentes
            num_pasos_final = max(num_pasos_actual, pasos_existentes)
            print(f"   📋 Pasos finales (máximo): {num_pasos_final}")
        else:
            num_pasos_final = num_pasos_actual
        
        # Generar fieldnames con el máximo número de pasos
        fieldnames = self._get_fieldnames(num_pasos_final)
        print(f"   📋 Columnas totales: {len(fieldnames)}")
        
        # Si hay registros existentes, adaptarlos al nuevo formato (con más columnas si es necesario)
        if existing_records:
            existing_fieldnames = list(existing_records[0].keys())
            
            # Si el número de columnas es diferente, adaptamos los registros existentes
            if len(existing_fieldnames) != len(fieldnames):
                print(f"   ⚠️ Diferente número de columnas: {len(existing_fieldnames)} vs {len(fieldnames)}")
                print(f"   📌 Adaptando registros existentes al nuevo formato (manteniendo datos)...")
                
                # Crear una copia de los registros existentes con el nuevo formato
                adapted_records = []
                for old_record in existing_records:
                    new_record = {}
                    # Copiar campos comunes (Tiempo, SN, Overall result)
                    for field in ['Tiempo', 'SN', 'Overall result']:
                        new_record[field] = old_record.get(field, '')
                    
                    # Copiar campos de pasos que existan en el registro antiguo
                    for field in fieldnames:
                        if field in old_record:
                            new_record[field] = old_record[field]
                        else:
                            new_record[field] = ''
                    
                    adapted_records.append(new_record)
                
                existing_records = adapted_records
                print(f"   ✅ {len(existing_records)} registros adaptados al nuevo formato")
        
        # Crear el registro con los valores actuales
        record = {
            'Tiempo': timestamp,
            'SN': sn,
            'Overall result': overall_result
        }
        
        # Agregar cada paso con su índice en las claves (hasta el máximo)
        for idx in range(1, num_pasos_final + 1):
            if idx <= len(steps_list):
                # Si el paso existe en la lista actual, usar sus valores
                step = steps_list[idx - 1]
                record[f'heightName_{idx}'] = step.get('name', '')
                record[f'heightResult_{idx}'] = step.get('status', '')
                record[f'heightLimitUp_{idx}'] = step.get('highLimit', '')
                record[f'heightLimitDown_{idx}'] = step.get('lowLimit', '')
                record[f'heightValue_{idx}'] = step.get('value', '')
            else:
                # Si el paso no existe, dejar campos vacíos
                record[f'heightName_{idx}'] = ''
                record[f'heightResult_{idx}'] = ''
                record[f'heightLimitUp_{idx}'] = ''
                record[f'heightLimitDown_{idx}'] = ''
                record[f'heightValue_{idx}'] = ''
        
        print(f"   📝 Nuevo registro con {len(record)} columnas")
        
        # Agregar nuevo registro a los existentes
        all_records = existing_records + [record]
        
        # Si excede el límite, mantener solo los últimos N registros
        if len(all_records) > self.max_records:
            all_records = all_records[-self.max_records:]
            print(f"   🔄 Se eliminaron registros antiguos. Manteniendo últimos {self.max_records}")
        
        # Escribir al archivo
        success = self._write_records(self.current_file_path, all_records, fieldnames)
        if success:
            self.records_count = len(all_records)
            print(f"\n✅ Trazabilidad guardada exitosamente")
            print(f"   SN: {sn}")
            print(f"   Overall result: {overall_result}")
            print(f"   Pasos registrados: {num_pasos_final} (máximo histórico)")
            print(f"   Pasos actuales: {len(steps_list)}")
            print(f"   Total registros en archivo: {self.records_count}")
            print(f"   Archivo: {self.current_file_path}")
            
            # Mostrar los pasos registrados
            print(f"\n   📋 Pasos registrados:")
            for i, step in enumerate(steps_list, 1):
                print(f"      {i}. {step.get('name')} = {step.get('value')} {step.get('units')} -> {step.get('status')}")
        else:
            print("❌ Error al guardar la trazabilidad")
        
        print(f"{'='*60}\n")
        return success

# Crear instancia global
traceability_manager = TraceabilityManager()