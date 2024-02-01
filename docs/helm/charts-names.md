nameOverride replaces the name of the chart in the Chart.yaml file, when this is used to construct Kubernetes object names. fullnameOverride completely replaces the generated name.

These come from the template provided by Helm for new charts. A typical object in the templates is named

> name: {{ include "<CHARTNAME>.fullname" . }}

If you install a chart with a deployment with this name, and where the Chart.yaml file specifies name: chart-name...

helm install release-name ., the Deployment will be named release-name-chart-name
helm install release-name . --set nameOverride=name-override, the Deployment will be named release-name-name-override
helm install release-name . --set fullnameOverride=fullname-override, the Deployment will be named fullname-override
The generated ...fullname template is (one code branch omitted, still from the above link)

```
{{- define "<CHARTNAME>.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
```

So if fullnameOverride is provided, that completely replaces the rest of the logic in the template. Otherwise the name is constructed from the release name and the chart name, where nameOverride overrides the chart name.