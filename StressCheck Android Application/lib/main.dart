import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: GetStartedScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
class GetStartedScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Stress Detector',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Color.fromARGB(255, 0, 0, 0),
        centerTitle: true,
      ),
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/background_image.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                height: 200,
                alignment: Alignment.topCenter,
                child: const CircleAvatar(
                  radius: 50,
                  backgroundImage: AssetImage('assets/avatar.jpg'),
                ),
              ),
              const Text(
                'Welcome to Stress Detector',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 20),
              const Text(
                'This app helps you detect stress levels\nby analyzing facial expressions\nusing AI',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 40),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => UploadScreen(),
                    ),
                  );
                },
                child: Text('Let\'s Get Started'),
                style: ElevatedButton.styleFrom(
                  primary: Colors.black,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
class UploadScreen extends StatefulWidget {
  @override
  _UploadScreenState createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _image;
  String? _result;

  Future getImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.getImage(source: ImageSource.gallery);

    setState(() {
      if (pickedFile != null) {
        _image = File(pickedFile.path);
      }
    });
  }

  Future uploadImage() async {
    if (_image == null) {
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('No Image Selected'),
            content: Text('Please select an image before uploading.'),
            actions: [
              ElevatedButton(
                child: Text('OK'),
                onPressed: () {
                  Navigator.of(context).pop();
                },
              ),
            ],
          );
        },
      );
      return;
    }

    var request = http.MultipartRequest(
      'POST',
      Uri.parse('http://10.200.221.195:5000/process_image'),
    );
    request.files.add(
      await http.MultipartFile.fromPath(
        'image',
        _image!.path,
      ),
    );

    var response = await request.send();
    if (response.statusCode == 200) {
      String result = await response.stream.bytesToString();
      Map<String, dynamic> jsonResult = jsonDecode(result);
      String stressLabel = jsonResult['stress_label'];
      String stressLevel = jsonResult['stress_level'];
      setState(() {
        _result = '$stressLabel';
        });
    } else {
      // ignore: use_build_context_synchronously
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Upload Failed'),
            content: Text('An error occurred when uploading the image please do it again'),
            actions: [
              ElevatedButton(
                child: Text('OK'),
                onPressed: () {
                  Navigator.of(context).pop();
                },
              ),
            ],
          );
        },
      );
    }
  }

@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: Text('Stress Detector'),
      backgroundColor: Color.fromARGB(255, 0, 0, 0),
      centerTitle: true,
    ),
    body: Container(
      decoration: const BoxDecoration(
        image: DecorationImage(
          image: AssetImage('assets/background_image.jpg'),
          fit: BoxFit.cover,
        ),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(height: 20),
            const Text(
              'Please upload a picture from your library for the AI to analyze',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            _image == null
                ? Text(
                    'No image selected.',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.normal,
                    ),
                  )
                : Image.file(
                    _image!,
                    width: 300,
                    height: 300,
                  ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: getImage,
              child: Text('Select Image'),
              style: ElevatedButton.styleFrom(
                primary: Colors.black,
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: uploadImage,
              child: Text('Upload Image'),
              style: ElevatedButton.styleFrom(
                primary: Colors.black,
              ),
            ),
            SizedBox(height: 20),
            if (_result != null)
              Text(
                'Result: $_result',
                style: TextStyle(fontSize: 18),
              ),
          ],
        ),
      ),
    ),
  );

}
}
