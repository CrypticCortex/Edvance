import { redirect } from "next/navigation"

export default function HomePage() {
  // Redirect to auth page for now
  redirect("/auth/login")
}
