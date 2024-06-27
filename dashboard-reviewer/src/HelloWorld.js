// Copyright 2021 Google LLC

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     https://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useEffect, useState, useContext } from 'react'
import { Space, ComponentsProvider, Span, Button, Text, Spinner, InputText } from '@looker/components'
import { ExtensionContext } from '@looker/extension-sdk-react'
import './styles.css' // Import your CSS file

/**
 * A simple component that uses the Looker SDK through the extension sdk to display a customized hello message.
 */

export const HelloWorld = () => {
  const { core40SDK } = useContext(ExtensionContext)
  const [message, setMessage] = useState()
  const [dashboardOptions, setDashboardOptions] = useState([])
  const [selectedDashboard, setSelectedDashboard] = useState('')
  const [reviewResponse, setReviewResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const initialize = async () => {
      try {
        const value = await core40SDK.ok(core40SDK.me())
        setMessage(`Hello, ${value.display_name}`);
        const dashboards = await core40SDK.ok(core40SDK.all_dashboards());
        console.log(dashboards)
        const dashboardOptionsMaps = dashboards.map(dashboard => ({
          id: dashboard.id,
          name: dashboard.title,
        }));
        console.log(dashboardOptionsMaps);
        setDashboardOptions(dashboardOptionsMaps)

      } catch (error) {
        setMessage('Error occured getting information about me!')
        console.error(error)
      }
    }
    initialize()
  }, [])

  const parseMarkdownBold = (text) => {
    const boldRegex = /\*\*(.*?)\*\*/g;
    return text.split(boldRegex).map((part, index) => {
      if (index % 2 === 1) {
        return <Text key={index} fontWeight="bold">{part}</Text>;
      } else {
        return part;
      }
    });
  };

  const handleSearchChange = async (e) => {
    setSearchQuery(e.target.value);
    if (e.target.value.length > 2) { // Start searching after 3 characters
      try {
        const dashboards = await core40SDK.ok(core40SDK.search_dashboards({ title: e.target.value }));
        const dashboardOptionsMaps = dashboards.map(dashboard => ({
          id: dashboard.id,
          name: dashboard.title,
        }));
        setDashboardOptions(dashboardOptionsMaps);
      } catch (error) {
        console.error('Error searching dashboards:', error);
      }
    } else {
      setDashboardOptions([]);
    }
  };

  const handleReviewClick = async () => {
    try {
      setLoading(true); // Start loading indicator
    console.log('Inside Handle Review')

    const dashboardData = await core40SDK.ok(core40SDK.dashboard_lookml(selectedDashboard))

    console.log('I am here', dashboardData)

    // We need call API
    const api = 'https://us-central1-best-hack-427512.cloudfunctions.net/explore-assistant-api'
    // Post Request, pass header X-Signature and body as dashboardData (JSON)

    const headers = {
      'Content-Type': 'application/json',
      'X-Signature': '<token>', // Replace with your actual signature header
    };

    const body = JSON.stringify(dashboardData);

    const response = await fetch(api, {
      method: 'POST',
      headers: headers,
      body: body
    });

    if (response.ok) {
      const data = await response.text(); // Read response as text
      setReviewResponse(data);
      console.log('API Response:', data);
      // Handle further actions if needed
    } else {
      console.error('Error:', response.statusText);
      // Handle error scenario
    }
   } finally {
    setLoading(false); // Stop loading indicator
   }
  }

  return (
    <>
      <ComponentsProvider>
      <div className="container">
      <div className="help-section">
        <h1 align = 'center'>Jupiter</h1>
        <h3 align = 'center'>Looker Dashboard Review Tool</h3>
        <p>Jupiter: Postman's Looker Dashboard Review Tool is poised to become an essential asset for the Looker community by automating and streamlining the dashboard review process.<br></br> <br></br>
            Using a simple interface, the tool provides instant feedback on improvements to metrics, as well as visual and text storytelling.
            Therefore, Jupiter eliminates the tedious and error-prone task of manual checks.
            This idea came from our own experiences discovering errors in crucial dashboards months after a small change to a tile or missing out on checks due to multiple dashboard review cycles. <br></br> <br></br>
            In its future scope, Jupiter aims to become a combination of AI-driven suggestions and rule-based validations.
            Admins will be able to provide runtime data, trust metrics, dashboard LookML etc. and add custom guidelines in an easy-to-use interface for guideline management.
            The tool can be customized to adhere to organizational guidelines, so that "best practices" do not live in a maze of documents, but are used to guide LookML developers realtime. <br></br> <br></br>
            Jupiter not only boosts productivity but also elevates the overall quality and consistency of dashboards, making it an indispensable tool for Looker users.
            -- Watch the video below for a demo on how to use this web app.
          </p>
    </div>
    <div className="form-section">
          <h2>Select Dashboard</h2>
          <select onChange={(e) => setSelectedDashboard(e.target.value)} className="select-dropdown">
            {dashboardOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>

    <div className="spacer"></div>

     <Button onClick={handleReviewClick} disabled={!selectedDashboard}>
            Review
      </Button>


      {loading && (
          <div style={{ display: 'flex', alignItems: 'center', marginTop: '10px' }}>
            <Spinner color="text" />
            <Text marginLeft="small" fontSize="large">Fetching review...</Text>
          </div>
        )}

      <div className="review-response">
            {reviewResponse && (
              <p>{parseMarkdownBold(reviewResponse)}</p>
            )}
        </div>
     </div>
     </div>
      </ComponentsProvider>
    </>
  )
}
