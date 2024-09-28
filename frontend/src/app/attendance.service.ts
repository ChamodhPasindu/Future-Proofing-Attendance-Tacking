import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AttendanceService {
  private baseUrl = 'http://127.0.0.1:5000';
  constructor(private http: HttpClient) {}

  registerCustomer(image: File, employeeId: string, employeeName: string): Observable<any> {
    const url = `${this.baseUrl}/register`;
    const formData: FormData = new FormData();
    formData.append('image', image, image.name);
    formData.append('tag', employeeId);
    formData.append('name', employeeName);

    const headers = new HttpHeaders();

    return this.http.post<any>(url, formData, { headers });
  }

  recognizeCustomer(image: File): Observable<any> {
    const url = `${this.baseUrl}/recognize`;
    const formData: FormData = new FormData();
    formData.append('image', image, image.name);

    const headers = new HttpHeaders();

    return this.http.post<any>(url, formData, { headers });
  }

  getAllEmployees(): Observable<any> {
    const url = `${this.baseUrl}/employees`;
    return this.http.get<any>(url);
  }

  getAllTodayAttendance(): Observable<any> {
    const url = `${this.baseUrl}/attendance/today`;
    return this.http.get<any>(url);
  }

  getEmployeeAttendance(employeeId: string, year: number, month: number): Observable<any> {
    const params = {employee_id:employeeId,year:year,month:month}
    return this.http.get<any>(this.baseUrl + `/attendance/employees`,{params});
  }

  dataURItoFile(dataURI: string, filename: string): File {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
  
    // Create a File from the Blob
    return new File([ab], filename, { type: mimeString, lastModified: Date.now() });
  }
}
