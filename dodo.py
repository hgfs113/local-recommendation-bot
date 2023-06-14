def task_gitclean():
    return {
            'actions': ['git clean -Xdf'],
           }

def task_html():
    return {
            'actions': ['sphinx-build doc _build'],
           }
 
