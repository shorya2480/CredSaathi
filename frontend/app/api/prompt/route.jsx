import { NextResponse } from "next/server";

export async function POST(request) {
    let { prompt } = await request.json();

    //implement AI logic here
    const AIresponse = "";

    return NextResponse.json({ AIresponse });
}