python manage.py graph_models repository --dot -S -o models.dot
dot -Tpng models.dot -omodels.png
rm models.dot

