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


Standard Labels
The following table defines common labels that Helm charts use. Helm itself never requires that a particular label be present. Labels that are marked REC are recommended, and should be placed onto a chart for global consistency. Those marked OPT are optional. These are idiomatic or commonly in use, but are not relied upon frequently for operational purposes.

Name	Status	Description
app.kubernetes.io/name	REC	This should be the app name, reflecting the entire app. Usually {{ template "name" . }} is used for this. This is used by many Kubernetes manifests, and is not Helm-specific.
helm.sh/chart	REC	This should be the chart name and version: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}.
app.kubernetes.io/managed-by	REC	This should always be set to {{ .Release.Service }}. It is for finding all things managed by Helm.
app.kubernetes.io/instance	REC	This should be the {{ .Release.Name }}. It aids in differentiating between different instances of the same application.
app.kubernetes.io/version	OPT	The version of the app and can be set to {{ .Chart.AppVersion }}.
app.kubernetes.io/component	OPT	This is a common label for marking the different roles that pieces may play in an application. For example, app.kubernetes.io/component: frontend.
app.kubernetes.io/part-of	OPT	When multiple charts or pieces of software are used together to make one application. For example, application software and a database to produce a website. This can be set to the top level application being supported.