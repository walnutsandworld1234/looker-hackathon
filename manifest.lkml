
application: dashboard-reviewer {
  label: "dashboard-reviewer"
  url: "https://localhost:8080/bundle.js"
  # file: "bundle.js
  entitlements: {
    external_api_urls : ["https://localhost:8080","https://us-central1-best-hack-427512.cloudfunctions.net"]
    core_api_methods: ["me", "dashboard", "all_dashboards", "dashboard_lookml", "search_dashboards"] #Add more entitlements here as you develop new functionality
  }
}
