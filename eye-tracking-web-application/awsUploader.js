export async function sendDataToAWS(dataToSend) {
    // Replace with your API endpoint or AWS Lambda function endpoint
    const endpoint = "https://jtq9ytgg2b.execute-api.us-east-1.amazonaws.com/prod/storeData";

    try {
        // Make sure dataToSend.body is a string, not an object
        if (typeof dataToSend.body !== 'string') {
            // Convert the object within body to a string
            dataToSend.body = JSON.stringify(dataToSend.body);
        }

        console.log(typeof dataToSend.body);  // This should now be "string"

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Send the stringified body directly
            body: JSON.stringify({ body: dataToSend.body }), // Wrap body in an additional object like your Postman request
        });

        if (!response.ok) {
            throw new Error(`Error sending data to AWS: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Data successfully sent to AWS:', data);
    } catch (error) {
        console.error('Error sending data to AWS:', error);
    }
}
