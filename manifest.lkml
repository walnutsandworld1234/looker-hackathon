project_name: "postman_dataverse"

application: my_review_extension {
  label: "My Review Extension"
  url: "https://localhost:8080/bundle.js"
  mount_points: {
    dashboard_tile: yes
  }
  entitlements: {
    local_storage: yes
    use_form_submit: yes
    core_api_methods: ["me"]
    external_api_urls: []
    oauth2_urls: []
    scoped_user_attributes: []
    global_user_attributes: []
  }
}
