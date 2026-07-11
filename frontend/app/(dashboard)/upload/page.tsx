import { Upload as UploadIcon } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function UploadPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Upload Statement</h2>
        <p className="text-gray-400 mt-1">Upload your bank PDF statements for AI parsing.</p>
      </div>

      <Card className="bg-[#1e1e2e] border-[#2a2a4e] text-white max-w-2xl">
        <CardHeader>
          <CardTitle>File Upload</CardTitle>
          <CardDescription className="text-gray-400">Supported formats: HDFC, SBI, ICICI, Axis, Kotak PDF & CSV</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-[#2a2a4e] rounded-xl p-12 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-[#2a2a4e]/20 transition-colors">
            <div className="p-4 bg-indigo-500/20 rounded-full mb-4">
              <UploadIcon className="w-8 h-8 text-indigo-400" />
            </div>
            <h3 className="text-lg font-medium mb-1">Drag and drop your file here</h3>
            <p className="text-sm text-gray-500 mb-6">or click to browse from your computer</p>
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
              Select File
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
