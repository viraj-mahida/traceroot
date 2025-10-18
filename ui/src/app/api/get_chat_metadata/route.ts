import { NextResponse } from "next/server";
import { GetChatMetadataRequest, ChatMetadata } from "@/models/chat";
import { createBackendAuthHeaders } from "@/lib/server-auth-headers";

export async function GET(
  request: Request,
): Promise<NextResponse<ChatMetadata | null>> {
  try {
    const url = new URL(request.url);
    const chat_id = url.searchParams.get("chat_id");

    if (!chat_id) {
      return NextResponse.json(null, { status: 400 });
    }

    const restApiEndpoint = process.env.REST_API_ENDPOINT;

    if (restApiEndpoint) {
      try {
        // Get auth headers (automatically uses Clerk's auth() and currentUser())
        const headers = await createBackendAuthHeaders();

        const apiUrl = `${restApiEndpoint}/v1/explore/get-chat-metadata?chat_id=${encodeURIComponent(chat_id)}`;
        const apiResponse = await fetch(apiUrl, {
          method: "GET",
          headers,
        });

        if (!apiResponse.ok) {
          throw new Error(
            `REST API call failed with status: ${apiResponse.status}`,
          );
        }

        const apiData: ChatMetadata = await apiResponse.json();

        // Convert timestamp from Python datetime string to number for consistency
        const processedData: ChatMetadata = {
          ...apiData,
          timestamp:
            typeof apiData.timestamp === "string"
              ? new Date(apiData.timestamp).getTime()
              : apiData.timestamp,
        };

        return NextResponse.json(processedData);
      } catch (apiError) {
        console.error("REST API call failed:", apiError);
        // Fall back to null response if REST API fails
        console.log("Falling back to null response due to API error");
      }
    }

    // Fallback to null response when REST_API_ENDPOINT is not set or API call fails
    return NextResponse.json(null);
  } catch (error) {
    console.error("Get Chat Metadata API Error:", error);

    return NextResponse.json(null, { status: 500 });
  }
}
