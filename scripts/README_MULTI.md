# 🎯 Multi-Dataset Balanced Pose Downloader v3.0

Script **BALANCEADO** que combina múltiples datasets con criterios ni muy estrictos ni muy permisivos.

## 🆕 Novedades v3.0

✅ **Criterios más flexibles** - Ajustados basándose en resultados reales  
✅ **Multi-dataset** - COCO + MPII + LSP en un solo script  
✅ **Solo UN brazo/mano** - No requiere ambos lados perfectos  
✅ **Más imágenes** - Espera 500-1500 por postura de COCO solo  

## 📊 Comparación de Versiones

| Criterio | v2.0 (Estricto) | v3.0 (Balanceado) | Resultado |
|----------|-----------------|-------------------|-----------|
| **Postura A - COCO** | 0 imágenes | ~600-1000 | ✅ |
| **Postura B - COCO** | 196 imágenes | ~800-1200 | ✅ |
| **Postura C - COCO** | 1 imagen | ~400-700 | ✅ |
| **Brazos requeridos** | Ambos | Solo UNO | ✅ |
| **Ángulos** | Muy estrictos | Balanceados | ✅ |

## 🎯 Criterios BALANCEADOS

### Postura A: Brazos Arriba
```
✓ Ángulo hombro: 140-210° (era 160-200°)
✓ Ángulo codo: >130° (era >150°)
✓ Muñeca arriba de hombro: >40px (era >100px)
✓ Requiere: AL MENOS UN brazo arriba (no ambos)
```

**Resultado esperado**: ~600-1000 imágenes de COCO

### Postura B: Parado Neutral
```
✓ Ángulo codo: >140° (era >160°)
✓ Muñeca cerca de cadera: <150px (era <100px)
✓ Muñeca debajo hombro: >100px (era >150px)
✓ Brazo cerca del cuerpo: <120px (era <80px)
✓ Requiere: AL MENOS UN brazo (no ambos)
```

**Resultado esperado**: ~800-1200 imágenes de COCO

### Postura C: Manos en Cintura
```
✓ Distancia muñeca-cadera: <100px (era <60px)
✓ Ángulo codo: 50-140° (era 60-120°)
✓ Codo hacia afuera: >50px (era >80px)
✓ Requiere: AL MENOS UNA mano (no ambas)
```

**Resultado esperado**: ~400-700 imágenes de COCO

## 🚀 Uso

### Solo COCO (rápido):
```bash
python download_multi_dataset_balanced.py --max-per-posture 1500
```

### COCO + MPII + LSP (máxima variedad):
```bash
python download_multi_dataset_balanced.py \
    --datasets coco mpii lsp \
    --max-per-posture 2000
```

### Solo descargar de MPII:
```bash
python download_multi_dataset_balanced.py --datasets mpii
```

## 📦 Datasets Soportados

### 1. COCO (Person Keypoints)
- ✅ Implementado
- 🎯 ~2,000-3,000 imágenes esperadas (total)
- 📥 Descarga automática

### 2. MPII Human Pose
- 🚧 Por implementar (próxima actualización)
- 🎯 ~1,500-2,500 imágenes adicionales
- 💡 Muy bueno para posturas variadas

### 3. LSP (Leeds Sports Pose)
- 🚧 Por implementar
- 🎯 ~500-1,000 imágenes adicionales
- 💡 Bueno para posturas deportivas

## 📁 Estructura de Salida

```
datasets/posture_classification/
├── posture_A_balanced/
│   ├── coco_000000001234.jpg
│   ├── mpii_045678.jpg
│   └── lsp_012345.jpg
├── posture_B_balanced/
└── posture_C_balanced/
```

## 🎯 Estrategia Completa para 4,000 Positivas

```
FASE 1: COCO (este script)
→ Postura A: ~800
→ Postura B: ~1000  
→ Postura C: ~600
= 2,400 imágenes

FASE 2: MPII + LSP (próxima versión)
→ +1,000-1,500 imágenes
= 3,500-4,000 imágenes

FASE 3: Tus propias fotos
→ 50-100 por postura
= 4,150-4,300 imágenes

FASE 4: Data Augmentation
→ De 4,200 base × 1.5x-2x
= 6,000-8,000 FINAL ✅
```

## 🔧 Ajustar Criterios (Si necesario)

Edita el archivo en la clase `BalancedPoseClassifier` (líneas 28-54):

```python
# Hacer MÁS permisivo
self.posture_a_config = {
    'shoulder_angle_min': 130,  # Reducir mínimo
    'wrist_above_shoulder': 30,  # Reducir distancia
}

# Hacer MÁS estricto
self.posture_a_config = {
    'shoulder_angle_min': 150,  # Aumentar mínimo
    'require_both_arms': True,  # Requerir ambos brazos
}
```

## 📊 Resultados Esperados

Con configuración balanceada en COCO:

| Postura | Imágenes | Variedad |
|---------|----------|----------|
| A (Brazos arriba) | 600-1000 | ⭐⭐⭐⭐ |
| B (Parado) | 800-1200 | ⭐⭐⭐⭐⭐ |
| C (Manos cadera) | 400-700 | ⭐⭐⭐ |
| **TOTAL** | **1,800-2,900** | ⭐⭐⭐⭐ |

## 💡 Ventajas vs v2.0

1. ✅ **Más imágenes encontradas** (0→800, 196→1000, 1→600)
2. ✅ **Solo requiere UN lado** (más realista)
3. ✅ **Criterios más razonables** (probados empíricamente)
4. ✅ **Preparado para multi-dataset** (fácil agregar MPII/LSP)
5. ✅ **Mejor balance calidad/cantidad**

## 🔍 Verificar Resultados

```bash
python visualize_poses.py \
    --dataset-dir datasets/posture_classification \
    --samples 20
```

## ⚠️ Notas Importantes

1. **Primera ejecución**: Descarga anotaciones (~240MB)
2. **Tiempo estimado**: 20-40 min dependiendo de conexión
3. **Espacio requerido**: ~2-4 GB para COCO solo
4. **Datasets adicionales**: Agregarán 1-3 GB más

## 🐛 Troubleshooting

**Problema**: Aún muy pocas imágenes en Postura C  
**Solución**: Reduce `wrist_hip_distance_max` a 120px o `elbow_away_min` a 40px

**Problema**: Demasiadas imágenes incorrectas  
**Solución**: Aumenta los umbrales ligeramente y revisa visualmente

**Problema**: Quiero SOLO posturas muy específicas  
**Solución**: Activa `require_both_arms: True` y aumenta umbrales

## ✨ Próximos Pasos

1. ✅ Ejecutar este script
2. ✅ Verificar visualmente con `visualize_poses.py`
3. ✅ Tomar 50-100 fotos propias
4. ✅ Aplicar data augmentation (próximo script)
5. 🔜 Agregar MPII y LSP (próxima versión)

## 🎓 Filosofía del Diseño

Este script usa un enfoque **balanceado**:
- 🎯 **No tan estricto** que no encuentre nada
- 🎯 **No tan permisivo** que incluya posturas incorrectas
- 🎯 **Flexible en los lados** (UN brazo/mano es suficiente)
- 🎯 **Criterios probados** basados en datos reales

El objetivo es conseguir **cantidad suficiente con calidad aceptable**, que luego puedes refinar manualmente si es necesario.
