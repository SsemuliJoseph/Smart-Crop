// The base URL for our backend (to be configured by backend team)
const API_URL = 'https://example-aws-api-gateway-url.amazonaws.com/prod';

/**
 * Reads the image file, converts to base64, and posts to API_URL + /detect
 * @param {string} imageBase64 - The base64 string of the image
 * @returns {object} JSON response from the server containing disease info
 */
export async function detectDisease(imageBase64) {
  try {
    const response = await fetch(`${API_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_base64: imageBase64,
        farmer_id: "farmer001"
      })
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    // Throws clear error messages on failure
    throw new Error(`Failed to detect disease: ${error.message}`);
  }
}

/**
 * Retrieves the history of disease scans for a specific farmer
 * @param {string} farmerId - The ID of the farmer
 * @returns {array} List of history records
 */
export async function getHistory(farmerId) {
  try {
    const response = await fetch(`${API_URL}/history/${farmerId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    // Throws clear error messages on failure
    throw new Error(`Failed to fetch history: ${error.message}`);
  }
}